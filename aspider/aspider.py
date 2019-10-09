"""A simple web crawler -- main driver program."""

import argparse
import asyncio
import sys
from . import crawling
from . import reporting
from . import routeing
from . import __version__
from .util import logger, fix_url, TESTING
import logging

ARGS = argparse.ArgumentParser(
    prog='aspider', description=f"An Asyncio Web crawler, version: {__version__}")


def setup_arg_parse():
    ARGS.add_argument(
        'roots', nargs='*',
        default=[], help='Root URL (may be repeated)')
    ARGS.add_argument(
        '--max_redirect', action='store', type=int, metavar='N',
        default=10, help='Limit redirection chains (for 301, 302 etc.)')
    ARGS.add_argument(
        '--max_tries', action='store', type=int, metavar='N',
        default=4, help='Limit retries on network errors')
    ARGS.add_argument(
        '--max_tasks', action='store', type=int, metavar='N',
        default=5, help='Limit concurrent connections')
    ARGS.add_argument(
        '-p', '--proxy', action='store', help='proxy to use for requesting')
    ARGS.add_argument(
        '-i', '--include', action='append', metavar='INCLUDE_REGEX',
        help='Include matching URLs')
    ARGS.add_argument(
        '-e', '--exclude', action='append', metavar='EXCLUDE_REGEX',
        help='Exclude matching URLs')
    ARGS.add_argument(
        '-o', '--output', action='store',
        help='output method to use [txt, csv, json, stream] ')
    ARGS.add_argument(
        '-c', '--count', action='store',
        help='limit count of urls to get')
    ARGS.add_argument(
        '--nostrict', action='store_false', dest='strict', help='Strict host matching (default)')
    ARGS.add_argument(
        '--no_parse_links', action='store_true', help='disable parsing links ')
    ARGS.add_argument(
        '-v', '--verbose', action='count', dest='level',
        default=1, help='Verbose logging (repeat for more verbose)')
    ARGS.add_argument(
        '-q', '--quiet', action='store_const', const=0, dest='level',
        default=1, help='Only log errors')


def parse_args():
    args, unkown = ARGS.parse_known_args()
    logger.debug('default args: %s', args)
    if not args.roots:
        print('Use --help for command line help')
        sys.exit(1)
    if TESTING:
        args.roots = []
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    logger.setLevel(levels[min(args.level, len(levels)-1)])
    return args


def exception_handler(loop, context):
    # first, handle with default handler
    loop.default_exception_handler(context)
    logger.debug('handle exception')
    exception = context.get('exception')
    logger.exception(exception)
    errors = (KeyboardInterrupt,)
    if isinstance(exception, errors):
        print(context)
        print('now exit loop')
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(
                *pending, loop=loop, return_exceptions=True))
        except:
            pass


async def do_async_report(router, crawler):
    await router.quit_event.wait()
    await asyncio.sleep(1)
    stats = reporting.gen_report(crawler)
    stats.report()


def download(loop=None, extra_args=None):
    """
    download links
    Parse arguments, set up event loop, run crawler, print report.

    Args:
        loop:EventLoop  -> eventloop to use for asyncio
        no_parse_links: bool -> disable parsing links
        extra_args: dict -> other args to use, or override default value
    """
    if extra_args:
        sys.argv.extend(extra_args.get('roots', []))
    args = parse_args()
    stats_report = None
    if extra_args:
        for key in extra_args:
            setattr(args, key, extra_args[key])
    logger.debug(args)
    print('args : ', args)
    out_loop = True if loop else False
    root_path = args.roots[0]
    router = routeing.get_router()
    logger.debug('resume the loop')
    router.resume(loop)
    router.add_root_path(root_path)
    logger.debug(f'set up router with root_path {root_path}')
    if not loop:
        loop = asyncio.get_event_loop()

    loop.set_exception_handler(exception_handler)

    roots = {fix_url(root) for root in args.roots}

    crawler = crawling.Crawler(roots,
                               exclude=args.exclude,
                               include=args.include,
                               output=args.output,
                               count=args.count,
                               proxy=args.proxy,
                               strict=args.strict,
                               max_redirect=args.max_redirect,
                               max_tries=args.max_tries,
                               max_tasks=args.max_tasks,
                               loop=loop,
                               no_parse_links=args.no_parse_links
                               )
    if out_loop:
        asyncio.ensure_future(crawler.crawl(), loop=loop)
        asyncio.ensure_future(do_async_report(router, crawler), loop=loop)
    else:
        try:
            loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.
        except KeyboardInterrupt:
            # sys.stderr.flush()
            pass
        finally:
            stats_report = reporting.gen_report(crawler)
    return stats_report


setup_arg_parse()
