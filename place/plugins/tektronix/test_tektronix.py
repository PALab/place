"""Basic testing for Tektronix oscilloscope"""
import socket
from unittest import TestCase
import unittest
import json
from place import scan

TEST_CONFIG = """
{
    "scan_type": "basic_scan",
    "updates": 5,
    "directory": "/tmp/place_tmp",
    "comments": "",
    "instruments": [
        {
            "module_name": "tektronix",
            "class_name": "DPO3014",
            "priority": 100,
            "config": {
                "plot": false,
                "record_length": 10000,
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
            scan.web_main(TEST_CONFIG)
        except socket.timeout:
            self.skipTest("Cannot communicate with Tektronix oscilloscope.")

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
