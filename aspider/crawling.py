"""A simple web crawler -- class implementing crawling logic."""

import asyncio
import cgi
from collections import namedtuple, OrderedDict
import re
import time
import sys
import urllib.parse
import datetime
from . import routeing
from . import outputing
from .util import logger, now_time
try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

import aiohttp  # Install with "pip install aiohttp".
from requests_html import HTML


router = routeing.get_router()


def lenient_host(host):
    parts = host.split('.')[-2:]
    return ''.join(parts)


def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)


FetchStatistic = namedtuple('FetchStatistic',
                            ['url',
                             'next_url',
                             'status',
                             'exception',
                             'size',
                             'content_type',
                             'encoding',
                             'num_urls',
                             'num_new_urls'])


class Crawler:
    """Crawl a set of URLs.

    This manages two sets of URLs: 'urls' and 'done'.  'urls' is a set of
    URLs seen, and 'done' is a list of FetchStatistics.
    """

    def __init__(self, roots,
                 # What to crawl.
                 exclude=None, include=None, output=None, strict=True, count=None,
                 proxy=None, max_redirect=10, max_tries=4,  # Per-url limits.
                 max_tasks=10, loop=None, no_parse_links=False):
        self.loop = loop or asyncio.get_event_loop()
        self.roots = roots
        self.exclude = exclude
        self.include = include
        self.output = output
        self.count = int(count) if count else None
        self.strict = strict
        self.proxy = proxy
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.task_exit_counter = 0
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        self.done = []
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.root_domains = set()
        self.no_parse_links = no_parse_links
        for root in roots:
            parts = urllib.parse.urlparse(root)
            host, port = urllib.parse.splitport(parts.netloc)
            if not host:
                continue
            if re.match(r'\A[\d\.]*\Z', host):
                self.root_domains.add(host)
            else:
                host = host.lower()
                if self.strict:
                    self.root_domains.add(host)
                else:
                    self.root_domains.add(lenient_host(host))
        for root in roots:
            self.add_url(root)
        self.t0 = time.time()
        self.t1 = None
        self.output_file = self.get_file()

    @asyncio.coroutine
    def close(self):
        """Close resources."""
        yield from self.session.close()

    def host_okay(self, host):
        """Check if a host should be crawled.

        A literal match (after lowercasing) is always good.  For hosts
        that don't look like IP addresses, some approximate matches
        are okay depending on the strict flag.
        """
        host = host.lower()
        if host in self.root_domains:
            return True
        if re.match(r'\A[\d\.]*\Z', host):
            return False
        if self.strict:
            return self._host_okay_strictish(host)
        else:
            return self._host_okay_lenient(host)

    def _host_okay_strictish(self, host):
        """Check if a host should be crawled, strict-ish version.

        This checks for equality modulo an initial 'www.' component.
        """
        host = host[4:] if host.startswith('www.') else 'www.' + host
        return host in self.root_domains

    def _host_okay_lenient(self, host):
        """Check if a host should be crawled, lenient version.

        This compares the last two components of the host.
        """
        return lenient_host(host) in self.root_domains

    def record_statistic(self, fetch_statistic):
        """Record the FetchStatistic for completed / failed URL."""
        self.done.append(fetch_statistic)

    def parse_text(self, url, text):
        '''
        call callback func on route
        '''
        route, args = router.match(url)
        if route:
            route.call(text, **args)

    @asyncio.coroutine
    def parse_links(self, response):
        """Return a FetchStatistic and list of links."""
        links = set()
        content_type = None
        encoding = None
        body = yield from response.read()

        if response.status == 200:
            content_type = response.headers.get('content-type')
            pdict = {}

            if content_type:
                content_type, pdict = cgi.parse_header(content_type)

            encoding = pdict.get('charset', 'utf-8')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text(errors='ignore')

                # Replace href with (?:href|src) to follow image links.
                urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''',
                                      text))
                if urls:
                    logger.debug('got %r distinct urls from %r',
                                 len(urls), response.url)
                for url in urls:
                    normalized = urllib.parse.urljoin(str(response.url), url)
                    defragmented, frag = urllib.parse.urldefrag(normalized)
                    if self.url_allowed(defragmented):
                        links.add(defragmented)

                # parse text
                self.parse_text(str(response.url), text)

                # do outing
                self.handle_output(str(response.url), text)

        stat = FetchStatistic(
            url=response.url,
            next_url=None,
            status=response.status,
            exception=None,
            size=len(body),
            content_type=content_type,
            encoding=encoding,
            num_urls=len(links),
            num_new_urls=len(links - self.seen_urls))

        return stat, links

    def handle_output(self, url, text):
        if self.output:
            d = self.parse_output(url, text)
            logger.info(f'write item: {url}')
            outputing.do_write(self.output, d, self.output_file)

    def parse_output(self, url, text):
        html = HTML(html=text)
        title_ele = html.find('title', first=True)
        d = OrderedDict()
        d['title'] = title_ele.text
        d['url'] = url
        d['datetime'] = now_time()
        d['text'] = text
        return d

    def get_file(self):
        '''
        generate a file name for output
        '''
        domains = list(self.root_domains)
        dt = datetime.datetime.now()
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        f_name = f'{domains[0]}-{dt_str}'
        if self.output:
            if self.output == 'stream':
                return None
            f_name += f'.{self.output}'
        return f_name

    @asyncio.coroutine
    def fetch(self, url, max_redirect):
        """Fetch one URL."""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                response = yield from self.session.get(
                    url, allow_redirects=False, proxy=self.proxy)

                if tries > 1:
                    logger.info('try %r for %r success', tries, url)

                break
            except aiohttp.ClientError as client_error:
                logger.info('try %r for %r raised %r',
                            tries, url, client_error)
                exception = client_error

            tries += 1
        else:
            # We never broke out of the loop: all tries failed.
            logger.error('%r failed after %r tries',
                         url, self.max_tries)
            self.record_statistic(FetchStatistic(url=url,
                                                 next_url=None,
                                                 status=None,
                                                 exception=exception,
                                                 size=0,
                                                 content_type=None,
                                                 encoding=None,
                                                 num_urls=0,
                                                 num_new_urls=0))
            return

        try:
            if is_redirect(response):
                location = response.headers['location']
                next_url = urllib.parse.urljoin(url, location)
                self.record_statistic(FetchStatistic(url=url,
                                                     next_url=next_url,
                                                     status=response.status,
                                                     exception=None,
                                                     size=0,
                                                     content_type=None,
                                                     encoding=None,
                                                     num_urls=0,
                                                     num_new_urls=0))

                if next_url in self.seen_urls:
                    return
                if max_redirect > 0:
                    logger.info('redirect to %r from %r', next_url, url)
                    self.add_url(next_url, max_redirect - 1)
                else:
                    logger.error('redirect limit reached for %r from %r',
                                 next_url, url)
            else:
                stat, links = yield from self.parse_links(response)
                self.record_statistic(stat)
                # disable parse links
                if not self.no_parse_links:
                    for link in links.difference(self.seen_urls):
                        # use router to verify links
                        if self.verify_url(link) or router.verify_url(link, url):
                            self.q.put_nowait((link, self.max_redirect))
                    self.seen_urls.update(links)
        except Exception as ex:
            logger.error(f'parse error: {url}')
            logger.exception(ex)
        finally:
            yield from asyncio.sleep(1)
            yield from response.release()

    @asyncio.coroutine
    def exit_on_empty_queue(self):
        if self.count and len(self.done) >= self.count:
            logger.warning(f'reach count: {self.count}, now quit')
            router.stop()

        if self.q.qsize() == 0:
            logger.warning('empty queue, now quit')
            yield from self.q.join()
            router.stop()

    @asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while router.is_running():
                url, max_redirect = yield from self.q.get()
                logger.debug(f'work on url {url}')
                assert url in self.seen_urls
                yield from self.fetch(url, max_redirect)
                self.q.task_done()
                yield from self.exit_on_empty_queue()

        except asyncio.CancelledError:
            logger.warning('canceling the worker')

    def url_allowed(self, url):
        parts = urllib.parse.urlparse(url)
        if parts.scheme not in ('http', 'https'):
            # logger.debug('skipping non-http scheme in %r', url)
            return False
        host, port = urllib.parse.splitport(parts.netloc)
        if not self.host_okay(host):
            # logger.debug('skipping non-root host in %r', url)
            return False
        return True

    def verify_url(self, url):
        if self.include:
            for pattern in self.include:
                if re.search(pattern, url):
                    logger.debug(
                        f'{url} match include pattern: {pattern}, allowed')
                    return True
        if self.exclude and re.search(self.exclude, url):
            logger.debug(
                f'{url} match exclude pattern: {self.exclude}, rejected')
            return False
        # default False
        return False

    def add_url(self, url, max_redirect=None):
        """Add a URL to the queue if not seen before."""
        if max_redirect is None:
            max_redirect = self.max_redirect
        logger.debug('adding %r %r', url, max_redirect)
        self.seen_urls.add(url)
        self.q.put_nowait((url, max_redirect))

    @asyncio.coroutine
    def crawl(self):
        """Run the crawler until all finished."""
        try:
            workers = [asyncio.Task(self.work(), loop=self.loop)
                       for _ in range(self.max_tasks)]
            self.t0 = time.time()
            # yield from asyncio.gather(*workers, loop=self.loop, return_exceptions=True)
            yield from router.quit_event.wait()
            for w in workers:
                w.cancel()
            self.t1 = time.time()
        except asyncio.CancelledError:
            logger.warning('canceling the crawler')
        finally:
            logger.warning('closing the crawler')
            yield from self.close()
