'''
use requests to make a simple spider
to get douban top 250 movies title.
'''

import requests
import re
from requests_html import HTML
import time

root_url = 'https://movie.douban.com/top250'

pages_list = []


def parse_page(text):
    html_page = HTML(html=text)
    title_css = '#content > div > div.article > ol > li > div > div.info > div.hd > a > span:nth-child(1)'
    titles = html_page.find(title_css)
    for t in titles:
        print(t.text)


def get_root():
    res = requests.get(root_url)
    text = res.text
    html_page = HTML(html=text, url=root_url)
    links = html_page.links
    pattern = '\?start=.+'
    for link in links:
        if re.search(pattern, link):
            pages_list.append(link)
    parse_page(text)


def main():
    get_root()
    while len(pages_list) > 0:
        link = pages_list.pop(0)
        # print(link)
        full_link = root_url + link
        res = requests.get(full_link)
        text = res.text
        parse_page(text)


if __name__ == "__main__":
    t1 = time.time()
    main()
    t2 = time.time()
    print('used {} seconds'.format(t2-t1))
