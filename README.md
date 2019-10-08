## aspider
    一个简单好用的Python 异步爬虫

## 简介

    aspider 是一个基于Python asyncio 开发的爬虫工具, 可以通过命令行使用, 不用写任何代码, 也可以调用api, 自定义具体爬取的规则.
    aspider的设计原则是专注于爬取网页, 本身不包含如解析文本, 数据存储等内容, 这些都可以利用很多已有的工具框架自行加上. aspider 参考了
    类似flask的路由装饰器的方法, 只需要定义一些方法, 每个方法用于爬取一个相应的正则路径.

    author: gxtrobot

## 系统设计原理
- 系统使用常用的生产者, 消费者模式, 生产者产生需要爬取的链接并加入队列, 消费者从队列获取链接进行爬取, 并解析其内容和链接, 调用相关的方法, 和用户自定义的方法, 符合要求的链接会加到队列, 这样只通过一个根路径就可以扩展到全站爬取
- 系统才用asyncio的并发协程, 每个并发协程同时担任消费者和生产者的指责, 通过一个queue(队列)进行交互
- 系统定义了一个路由(Router), 作为用户唯一需要使用的对象, 路由不需要新建, 系统只有一个Router对象, 直接获取就可以使用
- 用户所有自定义方法, 都通过路由提供的装饰器来实现, 例如route, 无需创建class或其他复杂的逻辑


## 安装

To install use pip:

    $ pip install aspider

Or clone the repo:

    $ git clone https://github.com/gxtrobot/aspider.git
    $ python setup.py install

## 开始使用

### 命令行方式
aspider 安装完成后可以直接通过命令 ```aspider``` 使用, 或 ```python -m aspider```
```
 aspider --help
usage: aspider [-h] [--max_redirect N] [--max_tries N] [--max_tasks N]
               [-p PROXY] [-i INCLUDE_REGEX] [-e EXCLUDE_REGEX] [-o OUTPUT]
               [-c COUNT] [--nostrict] [--no_parse_links] [-v] [-q]
               [roots [roots ...]]

An Asyncio Web crawler, version: 0.1.0

positional arguments:
  roots                 要爬取的网页路径(一般为跟路径), 可以有多个

optional arguments:
  -h, --help            显示帮助信息
  --max_tasks N         并发任务数, 默认为5个, 如需要可以提高
  -p PROXY, --proxy PROXY
                        代理使用, 例如 http://localhost:1080
  -i INCLUDE_REGEX, --include INCLUDE_REGEX
                        需要匹配爬取的网页路径正则, 匹配的网页链接将被加入爬取队列
  -o OUTPUT, --output OUTPUT
                        输出的方法, 目前支持这几种[txt, json, stream], stream为命令行输出
  -c COUNT, --count COUNT
                        限制爬取的数量, 如指定, 到限额后爬虫自动退出, 队列未完成的会取消
  --no_parse_links      禁止解析链接, 指定后, 只爬取命令行给定的roots链接, 不会跟踪解
                        页面包含的链接
  -v, --verbose         debug 消息数据, 可以有多个v (-v , -vv)
  -q, --quiet           静默输出, 只打印错误消息
```
### 命令行使用例子
- 豆瓣250电影抓取

运行以下命令, 将会爬取top250的10页html, 并存到json文件中

```
aspider https://movie.douban.com/top250 --include /top250.* --out json
```
不过这通常并没太大用处, 因为这样只是抓取完整的html, 只适合有时候需要抓取整个网页, 然后用其他工具处理, 或者不懂python 开发, 可以先用这个抓取网页, 然后用其他工具处理

保存的json文件是json line格式, 就是说每行是一个json对象, 读取时候要相应处理, 每读取一行, 将该行内容转为json对象, python 代码如下
```
def read_json_lines():
    file = 'top250.json'
    with open(file) as f:
        for line in f:
            d = json.loads(line)
            print(d.keys()
```

## API 介绍

### routing 模块 - Router 对象

- route(rule, verify_func=None, no_parse_links=False)
```
装饰器, 在用户自定义解析方法使用

Args:
  rule: 处理path的正则表达式, 可以包含参数, 使用'<>'包住参数名就可以, 例如 '/page/<no>', 这样用户自定义方法可以接收no参数

  verify_func: 可选, 用户路径验证方法, 如果提供可以自定义是否处理该路径, 方法签名为 verify_url(path), return True or False

  no_parse_links: 可选, 是否处理该页面上的其他链接, 如果需要关闭解析该页面链接, 可以设置为True

用户被装饰方法定义如下:

@router.route('/page/<no>', verify_page_path)
def process_page(text, path, no):

Args:
    text: 当前要解析页面的html代码, 可以使用其他框架如lxml, request_html, BeautifulSoup
    path: 可选, 如果有该参数, 系统会自动传递该path参数供使用
    其他参数, 装饰器的自定义参数

    注意: 前两个参数为系统自动提供, 顺序不能错, 用户自定义参数在前两个之后
```

### aspider 模块
该模块提供download方法启动爬虫

- download(loop=None, extra_args=None):
```
Args:
  loop - 用户提供asyncio loop对象, 一般不需要, 除非是在编写定时任务, 多线程使用, 这时候用户生成一个loop对象并传入
  extra_args - 其他参数, aspider 命令行使用的参数可以用该dict对象传入
  其中, 必须的是roots key, 对应为抓取跟路径, 是一个list

Returns:
  stats - 抓取过程统计对象, 包含抓取的网页数量, 完成时间等数据

example:

  options = {
        'roots': ['https://movie.douban.com/top250']
    }
  stats = aspider.download(extra_args=options)

```

### reporting 模块

- Stats 对象
该对象记录抓取过程的统计数据, 如抓取网页数量, 完成时间, 速度等

- report()
该方法打印这次抓取的记录报告

### API 调用爬虫例子

#### douban top250 电影抓取(代码在example 下))
1. 先取得router对象
2. 定义解析方法, 使用router.route装饰器, 提供一个参数为要解析的path正则表达式
3. 定义一个main方法启动爬虫就可以

```
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

```