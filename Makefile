PYTHON3=python3

testarg:
	$(PYTHON3) -m aspider https://www.cdnbus.bid -i /page/\d+ -i /[A-Z]+-[0-9]+ --count 3 -vv --out json

pep8:
	pep8 *.py

wc:
	grep -v '^ *\(#.*\)\?$$' crawling.py | wc -l

package:
	rm dist/*
	$(PYTHON3) setup.py sdist bdist_wheel

upload_test:
	$(PYTHON3) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	$(PYTHON3) -m twine upload dist/*

