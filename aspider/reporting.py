"""Reporting subsystem for web crawler."""

import time
import io


class Stats:
    """Record stats of various sorts."""

    def __init__(self):
        self.stats = {}
        self.summary = {}
        self.strbuff = io.StringIO()

    def add(self, key, count=1):
        self.stats[key] = self.stats.get(key, 0) + count

    def report(self, file=None):
        print('*** Report ***', file=file)

        self.strbuff.seek(0)
        print(self.strbuff.read())

        for key, count in sorted(self.stats.items()):
            print('%10d' % count, key, file=file)

        print('Finished', self.summary['finished'],
              'urls in %.3f secs' % self.summary['used_time'],
              '(max_tasks=%d)' % self.summary['max_tasks'],
              '(%.3f urls/sec/task)' % self.summary['speed'],
              file=file)
        print('Todo:', self.summary['todo'], file=file)
        print('Done:', self.summary['finished'], file=file)
        print('Date:', self.summary['date'], 'local time', file=file)
        print("\n*** ALL DONE NOW ***\n")


def gen_report(crawler):
    """Print a report on all completed URLs."""
    t1 = crawler.t1 or time.time()
    dt = t1 - crawler.t0
    if dt and crawler.max_tasks:
        speed = len(crawler.done) / dt / crawler.max_tasks
    else:
        speed = 0
    stats = Stats()
    try:
        show = list(crawler.done)
        show.sort(key=lambda _stat: str(_stat.url))
        for stat in show:
            url_report(stat, stats, file=stats.strbuff)
    except KeyboardInterrupt:
        print('\nInterrupted', file=file)

    stats.summary['finished'] = len(crawler.done)
    stats.summary['used_time'] = dt
    stats.summary['max_tasks'] = crawler.max_tasks
    stats.summary['speed'] = speed
    stats.summary['todo'] = crawler.q.qsize()
    stats.summary['date'] = time.ctime()
    return stats


def url_report(stat, stats, file=None):
    """Print a report on the state for this URL.

    Also update the Stats instance.
    """
    if stat.exception:
        stats.add('fail')
        stats.add('fail_' + str(stat.exception.__class__.__name__))
        print(stat.url, 'error', stat.exception, file=file)
    elif stat.next_url:
        stats.add('redirect')
        print(stat.url, stat.status, 'redirect', stat.next_url,
              file=file)
    elif stat.content_type == 'text/html':
        stats.add('html')
        stats.add('html_bytes', stat.size)
        print(stat.url, stat.status,
              stat.content_type, stat.encoding,
              stat.size,
              '%d/%d' % (stat.num_new_urls, stat.num_urls),
              file=file)
    else:
        if stat.status == 200:
            stats.add('other')
            stats.add('other_bytes', stat.size)
        else:
            stats.add('error')
            stats.add('error_bytes', stat.size)
            stats.add('status_%s' % stat.status)
        print(stat.url, stat.status,
              stat.content_type, stat.encoding,
              stat.size,
              file=file)
