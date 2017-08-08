"""Basic testing for stages"""
from unittest import TestCase
import unittest
import json
from place import scan


TEST_LONG_STAGE = """
{
"updates": 2,
"comments": "test long stage",
"modules": [{
    "module_name": "xps_control",
    "class_name": "LongStage",
    "priority": 20,
    "config": {
        "start": 0,
        "increment": 0.2 }}]
}
"""

class TestStages(TestCase):
    """Test class"""
    def test0001_json_init(self):
        """Test that JSON is processing our string correctly"""
        dat = json.loads(TEST_LONG_STAGE)
        self.assertEqual(dat, json.loads(json.dumps(dat)))

    def test0002_move_stages(self):
        """Test that we can move the stage a bit"""
        self.skipTest("Not performing this test yet")
        scan.web_main(TEST_LONG_STAGE)

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
