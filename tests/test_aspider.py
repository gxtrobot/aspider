import json
from aspider import aspider


def test_args1():
    '''
    pass roots to aspider
    '''
    roots = ['https://www.cdnbus.bid',
             'https://www.cdnbus.in', 'https://www.javbus.icu']
    extra_args = {
        'roots': roots,
        'no_parse_links': True,
        'count': 10
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args2():
    '''
    pass roots to aspider
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'no_parse_links': True,
        'count': 10
    }
    aspider.download(extra_args=extra_args)


def test_args3():
    '''
    test proxy use
    '''
    roots = ['https://www.javbus.com', ]
    extra_args = {
        'roots': roots,
        'no_parse_links': True,
        'count': 10,
        'proxy': 'http://localhost:7890'
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args4():
    '''
    test quit when reach count limit
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'count': 5,
        'include': '/page/\d+'
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args4():
    '''
    test quit when reach count limit
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'count': 5,
        'include': '/page/\d+'
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args5():
    '''
    test quit when reach count limit
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'count': 10,
        'include': ['/[A-Z]+-[0-9]+', '/page/\d+']
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args6():
    '''
    test quit when reach count limit
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'count': 5,
        'include': ['/[A-Z]+-[0-9]+'],
        'output': 'txt'
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_args7():
    '''
    test write json
    '''
    roots = ['https://www.cdnbus.bid', ]
    extra_args = {
        'roots': roots,
        'count': 5,
        'include': ['/[A-Z]+-[0-9]+'],
        'output': 'json'
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()


def test_read_json():
    f_name = 'www.cdnbus.bid-2019-10-04 09:49:18.json'
    with open(f_name) as f:
        content = f.readlines()
        for line in content:
            item = json.loads(line)
            print(item['url'], item['datetime'])
