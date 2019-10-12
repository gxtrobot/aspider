# Sample Test passing with nose and pytest
import json


def test_pass():
    assert True, "dummy sample test"


def test_read_json_lines():
    file = 'top250.json'
    with open(file) as f:
        for line in f:
            d = json.loads(line)
            print(d.keys())
