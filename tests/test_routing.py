from aspider import aspider
from aspider.routeing import get_router

router = get_router()


def test_routing1():
    '''
    pass roots to aspider
    '''
    @router.route('/page/\d+')
    def parse_page(text, path):
        print(path)

    @router.route('/[A-Z]+-[0-9]+', no_parse_links=True)
    def parse_item(text, path):
        print(path)

    roots = ['https://www.cdnbus.bid/page/2']
    extra_args = {
        'roots': roots,
        'count': 40
    }
    stats_report = aspider.download(extra_args=extra_args)
    stats_report.report()
