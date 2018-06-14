"""Basic testing for the Counter"""
from unittest import TestCase
import json
from placeweb.worker import start_experiment


TEST_COUNTER = """
{
    "updates": 25,
    "directory": "/tmp/test_place_demo",
    "comments": "test0002_basic_counter from test_place_demo.py",
    "modules": [
        {
            "module_name": "place_demo",
            "class_name": "PlaceDemo",
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
        start_experiment(json.loads(TEST_COUNTER))
