"""Basic testing for the Counter"""
from unittest import TestCase
import json
from place import experiment


TEST_COUNTER = """
{
    "updates": 25,
    "directory": "/tmp/place_test_counter",
    "comments": "test0002_basic_counter from test_counter.py",
    "modules": [
        {
            "module_name": "counter",
            "class_name": "Counter",
            "priority": 10,
            "config": {
                "sleep_time": 0,
                "plot": false
            }
        }
    ]
}
"""

class TestCounter(TestCase):
    """Test class"""
    def test0001_basic_json(self):
        """Test that JSON is processing our string correctly"""
        dat = json.loads(TEST_COUNTER)
        self.assertEqual(dat, json.loads(json.dumps(dat)))

    def test0002_basic_counter(self): #pylint: disable=no-self-use
        """Test that we can perform an experiment with JSON input"""
        experiment.web_main(TEST_COUNTER)
