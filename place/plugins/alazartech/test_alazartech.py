"""Basic testing for AlazarTech card"""
from unittest import TestCase
import unittest
import json
from placeweb.worker import start_experiment
try:
    from . import atsapi as ats
except ImportError:
    pass


TEST_STR_660 = """
{
"updates": 1,
"directory": "/tmp/place_tmp",
"comments": "test ATS660",
"modules":
    [
        {
        "module_name": "alazartech",
        "class_name": "ATS660",
        "priority": 99,
        "config":
            {
            "clock_source": "INTERNAL_CLOCK",
            "sample_rate": "SAMPLE_RATE_10MSPS",
            "clock_edge": "CLOCK_EDGE_RISING",
            "decimation": 0,
            "analog_inputs":
                [
                    {
                    "input_channel": "CHANNEL_A",
                    "input_coupling": "DC_COUPLING",
                    "input_range": "INPUT_RANGE_PM_800_MV",
                    "input_impedance": "IMPEDANCE_50_OHM"
                    }
                ],
            "trigger_operation": "TRIG_ENGINE_OP_J",
            "trigger_engine_1": "TRIG_ENGINE_J",
            "trigger_source_1": "TRIG_FORCE",
            "trigger_slope_1": "TRIGGER_SLOPE_POSITIVE",
            "trigger_level_1": 128,
            "trigger_engine_2": "TRIG_ENGINE_K",
            "trigger_source_2": "TRIG_FORCE",
            "trigger_slope_2": "TRIGGER_SLOPE_POSITIVE",
            "trigger_level_2": 128,
            "pre_trigger_samples": 0,
            "post_trigger_samples": 1024,
            "records": 32,
            "average": true,
            "plot": "no"
            }
        }
    ]
}
"""
TEST_STR_9440 = """
{
"updates": 1,
"directory": "/tmp/place_tmp",
"comments": "test ATS9440",
"modules":
    [
        {
        "module_name": "alazartech",
        "class_name": "ATS9440",
        "priority": 99,
        "config":
            {
            "clock_source": "INTERNAL_CLOCK",
            "sample_rate": "SAMPLE_RATE_10MSPS",
            "clock_edge": "CLOCK_EDGE_RISING",
            "decimation": 0,
            "analog_inputs":
                [
                    {
                    "input_channel": "CHANNEL_A",
                    "input_coupling": "DC_COUPLING",
                    "input_range": "INPUT_RANGE_PM_400_MV",
                    "input_impedance": "IMPEDANCE_50_OHM"
                    }
                ],
            "trigger_operation": "TRIG_ENGINE_OP_J",
            "trigger_engine_1": "TRIG_ENGINE_J",
            "trigger_source_1": "TRIG_FORCE",
            "trigger_slope_1": "TRIGGER_SLOPE_POSITIVE",
            "trigger_level_1": 128,
            "calculated_trigger_value_1": "0.000",
            "trigger_engine_2": "TRIG_ENGINE_K",
            "trigger_source_2": "TRIG_DISABLE",
            "trigger_slope_2": "TRIGGER_SLOPE_POSITIVE",
            "trigger_level_2": 128,
            "calculated_trigger_value_2": "0.000",
            "pre_trigger_samples": 0,
            "post_trigger_samples": 1024,
            "records": 32,
            "average": true,
            "plot": "no"
            }
        }
    ]
}
"""

class TestOsciCardUtilities(TestCase):
    """Test class"""
    def test0002_json_init(self):
        """Test that JSON is processing our string correctly"""
        dat = json.loads(TEST_STR_660)
        self.assertEqual(dat, json.loads(json.dumps(dat)))
        dat = json.loads(TEST_STR_9440)
        self.assertEqual(dat, json.loads(json.dumps(dat)))

    def test0003_json_test1(self):
        """Test that we can perform a point test with JSON input"""
        try:
            board = ats.Board()
        except Exception as err: # pylint: disable=broad-except
            if "Board" in str(err) and "not found" in str(err):
                self.skipTest("No Alazar board detected.")
            else:
                self.skipTest(err)
        name = ats.boardNames[board.type]
        del board
        if name == 'ATS660':
            start_experiment(json.loads(TEST_STR_660))
        elif name == 'ATS9440':
            start_experiment(json.loads(TEST_STR_9440))
        else:
            self.skipTest("No test for {} board".format(name))


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
