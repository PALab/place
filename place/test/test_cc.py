'''
Test for the Continuous Controller
'''
from warnings import warn

from place.automate.osci_card.c_controller import ContinuousController
from place.alazartech.atsapi import SAMPLE_RATE_100KSPS, CHANNEL_A

try:
    control = ContinuousController()
except Exception: #pylint: disable=broad-except
    warn('No ATS card detected. Skipping controller test.')
    exit()
try:
    control.create_input()
except RuntimeError:
    warn('This card does not support asychronous ADMA. Skipping test.')
    exit()
control.setSampleRate(SAMPLE_RATE_100KSPS)
control.setCaptureDurationTo(1)
control.start_capture()
control.readData()
data = control.getDataAtOnce(CHANNEL_A)
