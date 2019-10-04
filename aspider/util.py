'''
some helper funcs like logging set up
'''

import logging
import os
import datetime

logger = logging.getLogger("aspider")
TESTING = False


def setup_logging():
    handler = logging.StreamHandler()
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s \n %(message)s '
    fmter = logging.Formatter(fmt)
    handler.setFormatter(fmter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)


def check_testing():
    global TESTING
    if os.getenv('TESTING'):
        TESTING = True
        logger.setLevel(logging.DEBUG)


def fix_url(url):
    """Prefix a schema-less URL with http://."""
    if '://' not in url:
        url = 'http://' + url
    return url


def now_time():
    fmt = '%Y-%m-%d %H:%M:%S'
    now = datetime.datetime.now().strftime(fmt)
    return now


def init():
    setup_logging()
    check_testing()


init()
