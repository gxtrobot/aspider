'''
例子: douban top 250 电影名单爬取
'''
from collections import namedtuple
from aspider.routeing import get_router
from aspider import aspider
from requests_html import HTML

Movie = namedtuple('Movie', ['rank', 'score', 'title'])

router = get_router()

root_url = 'https://movie.douban.com/top250'

movies_250 = []


@router.route('/top250\?start.+')
def process_page(text):
    html = HTML(html=text)
    item_css = '#content  ol.grid_view > li'
    items = html.find(item_css)
    rank_css = 'em'
    title_css = '.info  span.title'
    score_css = '.info  .rating_num'
    for item in items:
        rank = int(item.find(rank_css, first=True).text)
        title = item.find(title_css, first=True).text
        score = float(item.find(score_css, first=True).text)
        movies_250.append(Movie(rank, score, title))


def main():
    options = {
        'roots': [root_url]
    }
    stats = aspider.download(extra_args=options)
    stats.report()
    fname = 'top250.txt'
    sorted_movies_250 = sorted(movies_250, key=lambda m: m.rank)
    with open(fname, 'w') as f:
        for movie in sorted_movies_250:
            print(f'#{movie.rank:<10} {movie.score:<10.2f} - {movie.title}')
            print(f'#{movie.rank:<10} {movie.score:<10.2f} - {movie.title}', file=f)


if __name__ == "__main__":
    main()
