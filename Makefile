PYTHON3=python3

javbus:
	$(PYTHON3) example/bus_spider.py https://www.cdnbus.bid

pep8:
	pep8 *.py

wc:
	grep -v '^ *\(#.*\)\?$$' crawling.py | wc -l
