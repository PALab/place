'''
This module contains an implementation of an AbstractTriggeredController
'''
from math import ceil
from time import sleep
from ctypes import create_string_buffer

from place.automate.osci_card.utility import (
    convert_raw_data_to_ints,
    getValueOfConstantWithName
    )
from place.automate.osci_card.controller import AbstractTriggeredController

class TriggeredRecordingSingleModeController(AbstractTriggeredController):
    """
    This controller saves the acquired data first on the card memory and
    transfers it to the program when the acquisition is finished.

    *DO NOT USE* this controller if not necessary. Probably,
    TriggeredRecordingController is a good alternative.
    """
    def __init__(self, **kwds):
        super(TriggeredRecordingSingleModeController, self).__init__(**kwds)
        self.dependent_functions = [self._setClock, self._setSizeOfCapture]
        self.recordsPerCapture = 5
        print("It is strongly recommended to use the DualMode controllers. " +
              "This controller sometimes delivers wrong data (all prior " +
              "observations showed that the bad data is at the lower limit of " +
              "the input range).")
        self.bytes_per_sample = 0
        self.bytes_per_buffer = 0

    def readData(self, channel):
        if self.busy():
            print("The card is not yet ready.")
            return
        data_buffer = create_string_buffer(self.bytes_per_buffer)
        self.data = {}
        for channel in self.channels.keys():
            if self.channels[channel]:
                self.data[channel] = []
        for record in range(self.recordsPerCapture):
            for channel in self.channels.keys():
                if self.channels[channel]:
                    self.read(
                        getValueOfConstantWithName(channel),
                        data_buffer,
                        self.bytes_per_sample,
                        record + 1,
                        - (self.preTriggerSamples),
                        self.samplesPerRecord
                        )
                    self.data[channel].append(convert_raw_data_to_ints(data_buffer.raw)[:-16])
        for channel in self.data.keys():
            self.data[channel] = self._processData(self.data[channel], channel)

    def waitForEndOfCapture(self, updateInterval=0.1):
        while self.busy():
            if updateInterval > 0:
                print("busy")
                sleep(updateInterval)
            else:
                sleep(-updateInterval)

    def setRecordsPerCapture(self, recordsPerCapture):
        self.recordsPerCapture = recordsPerCapture
        if not self.configureMode:
            self._run_dependent_configuration(self._setSizeOfCapture)

    def getApproximateDuration(self):
        return  int(float(self.samplesPerRecord) * self.recordsPerCapture / self.samplesPerSec)

    def _setSizeOfCapture(self):
        # Get the maximum number of samples per channel
        # from the board and compare it to the requested number
        max_samples_per_channel, bits_per_sample = self.getMaxSamplesAndSampleSize()
        if max_samples_per_channel < self.samplesPerRecord:
            raise Exception(
                "this card does not allow to use so many samples:" +
                str(self.samplesPerRecord))

        self.bytes_per_sample = int(ceil(bits_per_sample / 8.0))

        # Calculate the size of a record buffer in bytes
        # Note that the buffer must be at least 16 samples larger than the transfer size
        self.bytes_per_buffer = int(self.bytes_per_sample * self.samplesPerRecord + 16)

        self.setRecordSize(
            self.preTriggerSamples,
            self.postTriggerSamples
            )

        self.setRecordCount(self.recordsPerCapture)

        self.readyForCapture = True
