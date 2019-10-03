import os
from aspider.util import logger


def test_logger():
    logger.debug('test')
    logger.warning('test')


def test_testing_flag():
    assert os.getenv('TESTING') is not None
    print(os.getenv('TESTING'))
