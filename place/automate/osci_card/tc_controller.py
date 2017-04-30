"""The Triggered Continuous Controller Class"""
from math import ceil

from .controller import AbstractTriggeredADMAController

class TriggeredContinuousController(AbstractTriggeredADMAController):
    """This controller shall be used when data has to be acquired after
    trigger events.

    In the simplest scenario use the controller like this:
        control = TriggeredContinuousController()
        control.create_input()
        control.setSampleRate(ats.SAMPLE_RATE_100KSPS)
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.start_capture()
        control.readData()
        data = control.getDataAtOnce(ats.CHANNEL_A)

    The card will record on Channel A with a sample rate of 100,000
    samples per second and trigger when 0 V is crossed with positive
    slope. The trigger events are assumed to be within 0.1 s. If there
    is no trigger event within this time a trigger event will be
    generated automatically. The data is structured in records where
    each record belongs to one trigger event. The returned data is one
    continuous list of samples.

    This controller does NOT allow preTriggerSamples.
    """
    def __init__(self, **kwds):
        super(TriggeredContinuousController, self).__init__(**kwds)
        # set variables for dependent functions
        self.dependent_functions = [self._setClock, self._setSizeOfCapture, self._prepare_capture]
        self.preTriggerSamples = 0
        self.samplesPerRecord = self.postTriggerSamples
        self.adma_flags = 0x1 | 0x200
        self.bytes_per_sample = 0
        self.bytes_per_buffer = 0

    def setSamplesPerRecord(
            self,
            samples=None,
            preTriggerSamples=None,
            postTriggerSamples=None):
        if preTriggerSamples != None:
            if preTriggerSamples != 0:
                raise Exception("The TriggeredContinuousController " +
                                "must not have preTriggerSamples!")
        super(TriggeredContinuousController, self).setSamplesPerRecord(
            samples=samples,
            preTriggerSamples=preTriggerSamples,
            postTriggerSamples=postTriggerSamples)

    def getApproximateDuration(self):
        return int(
            float(self.samplesPerRecord)
            * self.recordsPerBuffer * self.buffers_per_capture / self.samplesPerSec
            )

    def _setSizeOfCapture(self):
        """Defines the length of a record in samples.

        It is intended that either the absolute number of samples
        (keyword argument: samples) or both of the other keyword
        arguments are supplied.

        samples:            Absolute number of samples in one record. All
                            samples will be acquired after the trigger event.

        preTriggerSamples:  The number of samples in a record before the
                            trigger event.

        postTriggerSamples: The number of samples in a record after the trigger
                            event.
        """
        _, bits_per_sample = self.getMaxSamplesAndSampleSize()
        self.bytes_per_sample = int(ceil(bits_per_sample.value / 8.0))
        self._calc_bytes_per_buffer()
        self.set_record_size()
