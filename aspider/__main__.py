from .aspider import download, parse_args


def main():
    args = parse_args()
    stats_report = download(args=args)
    stats_report.report()


if __name__ == '__main__':
    main()
