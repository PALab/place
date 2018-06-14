"""Basic testing for Tektronix oscilloscope"""
from unittest import TestCase
import unittest
import json
from placeweb.worker import start_experiment

TEST_CONFIG = """
{
    "updates": 5,
    "directory": "/tmp/place_tmp",
    "comments": "",
    "modules": [
        {
            "module_name": "tektronix",
            "class_name": "DPO3014",
            "priority": 100,
            "config": {
                "plot": false,
                "force_trigger": true
            }
        }
    ]
}
"""

class TestOsci(TestCase):
    """Test class"""
    def test0001_json_init(self):
        """Test that JSON is processing our string correctly"""
        dat = json.loads(TEST_CONFIG)
        self.assertEqual(dat, json.loads(json.dumps(dat)))
        dat = json.loads(TEST_CONFIG)
        self.assertEqual(dat, json.loads(json.dumps(dat)))

    def test0002_json_test1(self):
        """Test that we can acquire data from the oscilloscope with JSON input"""
        try:
            start_experiment(json.loads(TEST_CONFIG))
        except OSError:
            self.skipTest("Cannot communicate with Tektronix oscilloscope.")
        except ValueError:
            self.skipTest('No IP address for oscilloscope.')

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
