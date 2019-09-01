#!/usr/bin/env python3.4

"""A simple web crawler -- main driver program."""

# TODO:
# - Add arguments to specify TLS settings (e.g. cert/key files).

import argparse
import asyncio
import logging
import sys
import nest_asyncio
from . import crawling
from . import reporting
from . import routeing

ARGS = argparse.ArgumentParser(description="Web crawler")
ARGS.add_argument(
    '--iocp', action='store_true', dest='iocp',
    default=False, help='Use IOCP event loop (Windows only)')
ARGS.add_argument(
    '--select', action='store_true', dest='select',
    default=False, help='Use Select event loop instead of default')
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
    default=10, help='Limit concurrent connections')
ARGS.add_argument(
    '--exclude', action='store', metavar='REGEX',
    help='Exclude matching URLs')
ARGS.add_argument(
    '--strict', action='store_true',
    default=True, help='Strict host matching (default)')
ARGS.add_argument(
    '--lenient', action='store_false', dest='strict',
    default=False, help='Lenient host matching')
ARGS.add_argument(
    '-v', '--verbose', action='count', dest='level',
    default=2, help='Verbose logging (repeat for more verbose)')
ARGS.add_argument(
    '-q', '--quiet', action='store_const', const=0, dest='level',
    default=2, help='Only log errors')


def fix_url(url):
    """Prefix a schema-less URL with http://."""
    if '://' not in url:
        url = 'http://' + url
    return url


def exception_handler(loop, context):
    print("")


def main(loop=None):
    """Main program.

    Parse arguments, set up event loop, run crawler, print report.
    """
    out_loop = True if loop else False
    args = ARGS.parse_args()
    if not args.roots:
        print('Use --help for command line help')
        return
    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels)-1)])

    root_path = args.roots[0]
    router = routeing.get_router()
    router.add_root_path(root_path)
    logging.debug(f'set up router with root_path {root_path}')
    if not loop:
        if args.iocp:
            from asyncio.windows_events import ProactorEventLoop
            loop = ProactorEventLoop()
            asyncio.set_event_loop(loop)
        elif args.select:
            loop = asyncio.SelectorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

    loop.set_exception_handler(exception_handler)

    roots = {fix_url(root) for root in args.roots}
    # nest_asyncio.apply(loop)

    crawler = crawling.Crawler(roots,
                               exclude=args.exclude,
                               strict=args.strict,
                               max_redirect=args.max_redirect,
                               max_tries=args.max_tries,
                               max_tasks=args.max_tasks,
                               loop=loop
                               )
    try:
        print(f'out_loop:{out_loop}')
        if out_loop:
            asyncio.ensure_future(crawler.crawl(), loop=loop)
        else:
            loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.
    except KeyboardInterrupt:
        # sys.stderr.flush()
        print('\nInterrupted\n')
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(
                *pending, loop=loop, return_exceptions=True))
        except:
            pass
    finally:
        reporting.report(crawler)
        print('ALL DONE')


if __name__ == '__main__':
    main()
