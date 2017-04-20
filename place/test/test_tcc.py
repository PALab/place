'''
Simple test for the TriggeredContinuousController
'''
from warnings import warn

from place.automate.osci_card.tc_controller import TriggeredContinuousController
from place.alazartech.atsapi.atsapi import SAMPLE_RATE_100KSPS, CHANNEL_A

try:
    control = TriggeredContinuousController()
except Exception: #pylint: disable=broad-except
    warn('No ATS card detected. Skipping controller test.')
    exit()
control.create_input()
control.setSampleRate(SAMPLE_RATE_100KSPS)
control.setTrigger()
control.setTriggerTimeout(0.1)
control.start_capture()
control.readData()
control.getDataAtOnce(CHANNEL_A)
