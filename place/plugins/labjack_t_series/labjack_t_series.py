'''LabJack T-Series'''
import time
from math import pi
from labjack import ljm
import numpy as np
import matplotlib.pyplot as plt
from place.plugins.instrument import Instrument
from place.basic_experiment import AbortExperiment
from place.config import PlaceConfig

# TODO: Read values from .place.cfg file into global variables


class LabJack(Instrument):
    '''LabJack T-series hardware module for PLACE'''

    def config(self, metadata, total_updates):
        raise AbortExperiment('LabJack config not implemented')

        # TODO: read user input from self._config

        # TODO: get handle to LabJack

        # TODO: stream setup

    def update(self, update_number, progress):
        raise AbortExperiment('LabJack update not implemented')

        # TODO: create waveform to send to output

        # TODO: check that values are safely in range

        # TODO: setup output signal

        # TODO: setup input signal

        # TODO: start stream

        # TODO: save data to PLACE NumPy record array

    def cleanup(self, abort=False):
        raise AbortExperiment('LabJack cleanup not implemented')

        # TODO: stop stream and close connection to LabJack
