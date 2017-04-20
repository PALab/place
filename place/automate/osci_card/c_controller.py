'''
Continuous Controller class
'''
from math import ceil
from numpy import linspace

from .controller import AbstractADMAController
from .utility import convert_raw_data_to_ints

class ContinuousController(AbstractADMAController):
    """
    This controller shall be used when data has to be acquired
    continuously.

    In the simplest scenario use the controller like this:
        control = ContinuousController()
        control.create_input()
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setCaptureDurationTo(1)
        control.start_capture()
        control.readData()
        data = control.getDataAtOnce("CHANNEL_A")

    The card will record on Channel A with a sample rate of 100,000
    samples per second.

    Note: Use setCaptureDuration to set the length of the capture in
    seconds.
    """
    def __init__(self, **kwds):
        super(ContinuousController, self).__init__(**kwds)
        # arbitrary
        self.samples_per_buffer = 1024 * 1024
        # set variables for dependent functions
        self.dependent_functions = [self._setClock, self._setSizeOfCapture, self._prepare_capture]
        self.adma_flags = 0x1 | 0x100 | 0x1000
        self.bytes_per_sample = 0
        self.bytes_per_buffer = 0

    def setCaptureDurationTo(self, seconds):
        """
        sets buffers_per_capture according to the desired capture time.
        """

        self.buffers_per_capture = int(
            ceil(float(seconds) * self.samplesPerSec / self.samples_per_buffer))
        self.recordsPerBuffer = 1

        if not self.configureMode:
            self._run_dependent_configuration(self._setSizeOfCapture)

    def getApproximateDuration(self):
        """
        return an approximate duration of the capture.
        """
        return  int(float(self.samples_per_buffer) * self.buffers_per_capture / self.samplesPerSec)

    def getTimes(self):
        """
        generates a time value to each sample value in a capture.

        The first sample has the time 0. Time values are spaced
        according to the sampling rate.
        """
        return linspace(
            0.0,
            float(self.buffers_per_capture * self.samples_per_buffer - 1) / self.samplesPerSec,
            self.buffers_per_capture * self.samples_per_buffer)

    def setSamplesPerBuffer(self, samples):
        """
        sets the samples contained in one buffer.

        Former tests recommend to choose 1024 or 1024*1024.
        """
        self.samples_per_buffer = samples

        if not self.configureMode:
            self._run_dependent_configuration(self._setSizeOfCapture)

    def _getPreTriggerSamples(self):
        return 0

    def _getSamplesPerRecord(self):
        return self.samples_per_buffer

    def _getRecordsPerBuffer(self):
        return 1

    def _getRecordsPerCapture(self):
        return self.buffers_per_capture

    def _processBuffer(self, data):
        data = convert_raw_data_to_ints(data)
        #pylint: disable=consider-iterating-dictionary
        for i, channel in enumerate(sorted(self.data.keys())):
            start = i * self.samples_per_buffer
            end = (i + 1) * self.samples_per_buffer
            self.data[channel].append(list(self._processData(data[start:end], channel)))

    def _setSizeOfCapture(self):
        """
        defines the length of a record in samples.

        It is intended that either the absolute number of samples
        (keyword argument: samples) or both of the other keyword
        arguments are supplied.

        :param samples: absolute number of samples in one record. All
                        samples will be acquired after the trigger
                        event.
        :param preTriggerSamples: the number of samples in a record
                                  before the trigger event
        :param postTriggerSamples: the number of samples in a record
                                   after the trigger event
        """
        _, bits_per_sample = self.getMaxSamplesAndSampleSize()
        self.bytes_per_sample = int(ceil(bits_per_sample.value / 8.0))
        self.bytes_per_buffer = int(self.bytes_per_sample * self.samples_per_buffer * self.channelCount)
