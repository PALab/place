"""Test for the Continuous Controller"""
from unittest import TestCase, main

from place.automate.osci_card.c_controller import ContinuousController
from place.alazartech.atsapi import SAMPLE_RATE_100KSPS, CHANNEL_A

class TestCC(TestCase):
    """Continuous Controller test class"""
    def test_continuous_controller(self):
        """Basic test"""
        try:
            control = ContinuousController()
        except Exception: #pylint: disable=broad-except
            self.skipTest('No ATS card detected. Skipping controller test.')
        try:
            control.create_input()
        except RuntimeError:
            self.skipTest('This card does not support asychronous ADMA. Skipping test.')
        control.setSampleRate(SAMPLE_RATE_100KSPS)
        control.setCaptureDurationTo(1)
        control.start_capture()
        control.readData()
        control.getDataAtOnce(CHANNEL_A)

if __name__ == '__main__':
    main(verbosity=2, buffer=True)
