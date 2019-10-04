from .aspider import download, parse_args


def main():
    stats_report = download()
    stats_report.report()


if __name__ == '__main__':
    main()
