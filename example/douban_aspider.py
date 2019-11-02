'''
use aspider to make a simple spider
to get douban top 250 movies title.
'''

from requests_html import HTML
from aspider import aspider
from aspider.routeing import get_router

router = get_router()

root_url = 'https://movie.douban.com/top250'


@router.route('/top250\?start=.+')
def parse_page(text):
    html_page = HTML(html=text)
    title_css = '#content > div > div.article > ol > li > div > div.info > div.hd > a > span:nth-child(1)'
    titles = html_page.find(title_css)
    for t in titles:
        print(t.text)


def main():
    options = {
        'roots': [root_url],
        'max_tasks': 10
    }
    stats = aspider.download(extra_args=options)
    stats.report()


if __name__ == "__main__":
    main()
