"""Simple test for the TriggeredContinuousController"""
from unittest import TestCase, main

from place.automate.osci_card.tc_controller import TriggeredContinuousController
from place.alazartech.atsapi import SAMPLE_RATE_100KSPS, CHANNEL_A

class TestTCC(TestCase):
    """Triggered Continuous Controller test class"""
    def test_trig_continuous_controller(self):
        """Basic test"""
        try:
            control = TriggeredContinuousController()
        except Exception: #pylint: disable=broad-except
            self.skipTest('No ATS card detected.')
        control.create_input()
        control.setSampleRate(SAMPLE_RATE_100KSPS)
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.start_capture()
        control.readData()
        control.getDataAtOnce(CHANNEL_A)

if __name__ == '__main__':
    main(verbosity=2, buffer=True)
