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
