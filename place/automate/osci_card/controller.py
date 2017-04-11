'''
This module allows the data acquisition with an Alazar oscilloscope card.

Update
-----------
Significant changes have been made to this file. These changes have
been made to link it to the Alazar Python wrappers supplied by Alazar.
In many ways, this file should be considered obsolete, although efforts
were made to maintain its functionality. Documentation beyond this point
may be outdated, but will be corrected as encountered. ~Paul (24/01/2017)

Quick Info
-----------

Use the TriggeredContinuousController by calling the following functions:

::

    control = TriggeredContinuousController()
    control.createInput()
    control.setSampleRate("SAMPLE_RATE_100KSPS")
    control.setTrigger()
    control.setTriggerTimeout(0.1)
    control.startCapture()
    control.readData()
    data = control.getDataAtOnce("CHANNEL_A")


The card will record on Channel A with a sample rate of 100,000 samples
per second and trigger when 0 V is crossed with positive slope. The
trigger events are assumed to be within 0.1 s. If there is no trigger
event within this time a trigger event will be generated automatically.
The data is structured in records where each record belongs to one
trigger event. The returned data is one continuous list of samples.


There are four different controllers available:

    - BasicController

    - TriggeredRecordingSingleModeController

    - TriggeredRecordingController

    - TriggeredContinuousController

    - ContinuousController

To get an idea of how to use the different Controllers you might want to
take a look at the test_controller module that is used for testing the
controllers.

The BasicController should only be used for basic testing, i.e.  can a
connection to the card be established.

The TriggeredRecordingSingleModeController can be used to record data,
which is saved to the cards memory, and when the recording is finished
the data can be transfered from the card to this module.  This
Controller should NOT be used. Use TriggeredRecordingController instead!

The TriggeredRecordingController is very flexible and can record data
when trigger events occur. It is a good choice if preTriggerSamples are
required. Otherwise use the TriggeredContinuousController

The TriggeredContinuousController is high performance controller for
recording data when trigger events occur. It allows higher sample rates
as the TriggeredRecordingController. No preTriggerSamples are possible.

The last Controller available is the ContinuousController. It just
records one long continuous record. There are no trigger events and the
samples are just separated by the inverse sampling rate.

This module uses the naming convention that private functions start with
an underscore. All functionality that is meant to be provided can
therefore be used by just using the functions that start NOT with an
underscore. If you look for some feature of some configuration look at
these functions.

This module was inspired by and uses code segments of Alazar example
files: /usr/local/AlazarTech/samples

Much of the functionality that is provided by the Alazar SDK is not
accessible via this module. If you are looking for a feature that is not
provided by this module, add it to the module or use access the SDK
directly using C++. Hints how to implement the missing might be found in
the respective files.

Remarks

Some configurations depend on each other. E.g. setting the number of
samples by defining the duration of the capture is not possible as long
as the sample rate is not set. Therefore, each controller has a
dependendFunctions list. When a function is called on which other
functions depend the functions in this list are executed in a defined
order. The exception to this rule is when the configureMode variable is
true. In this case the configuration is done only within this program
without telling the card. If startCapture realizes that the
configuration is not finished it triggers the execution of the
dependendFunctions.  Many Alazar functions have constants as arguments
that are defined in Alazar c header files. Most of these constants are
parsed using the parseConstants module and are afterwards available in
the AlazarCmd module (which is included as cons in this module).

@author: Henrik tom Woerden
Created on Jun 27, 2013
'''
# pylint: disable=invalid-name
from __future__ import print_function
from ctypes import cdll, c_uint32, c_char, c_void_p, create_string_buffer
from time import sleep
from math import ceil
from struct import unpack

import numpy as np

from place.alazartech import atsapi as ats
from place.automate.osci_card import utility as uti

__ATS_SUCCESS = 512

class DependendFunctionError(Exception):
    ''' Custom exception '''
    pass

class AlazarCardError(Exception):
    ''' Custom exception '''
    pass

class BasicController(object):
    '''
    Provides basic functionality to communicate with an Alazar card.

    This class is not intended for real usage; at most for testing. It
    is the base class of all more sophisticated controllers. Functions
    that are common in all controllers are defined in this class; some
    of them do nothing but raise an NotImplementedError Exception.
    '''
    def __init__(self, debugMode=False):
        self.card = ats.Board()
        self.libc = cdll.LoadLibrary('libc.so.6')
        self.inputRanges = {}
        self.configureMode = False
        self.sampleRate = "SAMPLE_RATE_1MSPS"
        self.dependendFunctions = []
        self.readyForCapture = False
        self.channelCount = 0
        self.debugMode = debugMode
        self.data = {}
        self.channelsPerBoard = 4
        self.channels = {"CHANNEL_A":False, "CHANNEL_B":False, "CHANNEL_C":False, "CHANNEL_D":False}
        self.samplesPerSec = 0

    def enableLED(self):
        ''' Turn on the board LED '''
        self.card.setLED(ats.LED_ON)

    def disableLED(self):
        ''' Turn off the board LED '''
        self.card.setLED(ats.LED_OFF)

    def setSampleRate(self, sampleRate):
        """
        sets variables that belong to the sample rate.
        """
        if sampleRate not in uti.getNamesOfConstantsThatStartWith("SAMPLE_RATE_"):
            raise Exception("Undefined Sample Rate in setClock")
        self.sampleRate = sampleRate
        self.samplesPerSec = uti.getSampleRateFrom(self.sampleRate)
        if not self.configureMode:
            self._runDependendConfiguration(self._setClock)

    def createInput(
            self,
            channel="CHANNEL_A",
            inputRange="INPUT_RANGE_PM_400_MV",
            AC=False,
            impedance=50):
        '''
        configures one channel for measurement.

        :param channel: string identifying the channel
                        (default "CHANNEL_A").

                        Possible strings are the channel names defined
                        in the c header file of the Alazar SDK.

                        Usually /usr/local/AlazarTech/include/AlazarCmd.h
        :param inputRanges: string identifying the input range of the
                            channel (default "INPUT_RANGE_PM_400_MV").

                            Possible strings are defined in the c header
                            file of the Alazar SDK.

                            Usually
                            /usr/local/AlazarTech/include/AlazarCmd.h
        :param AC: set True if AC coupling shall be used instead of DC
                   coupling
        :param impedance: define the impedance of the channel in Ohm.
                          If 1 is provided the impedance will be 1e6 Ohm.
        '''
        if channel not in uti.getNamesOfConstantsThatStartWith("CHANNEL_"):
            raise Exception("Undefined Channel in createInput")
        if channel not in self.channels:
            raise Exception(
                "Channel in createInput is defined but card is configured without this channel")
        if inputRange not in uti.getNamesOfConstantsThatStartWith("INPUT_RANGE_PM_"):
            raise Exception("Undefined Input Range in createInput")
        if self.debugMode:
            print("inputControl")
            print("    channel: {}".format(uti.getValueOfConstantWithName(channel)))
            print("    inputRange: {}".format(uti.getValueOfConstantWithName(inputRange)))
        if AC:
            coupling = ats.AC_COUPLING
        else:
            coupling = ats.DC_COUPLING
        if impedance == 50:
            imp = ats.IMPEDANCE_50_OHM
        elif impedance == 75:
            imp = ats.IMPEDANCE_75_OHM
        elif impedance == 300:
            imp = ats.IMPEDANCE_300_OHM
        elif impedance == 1:
            imp = ats.IMPEDANCE_1M_OHM
        else:
            raise Exception("No valid impedance value")
        self.inputRanges[channel] = uti.getInputRangeFrom(inputRange)
        print("inputControl({}, {}, {}, {})".format(
            channel,
            coupling,
            inputRange,
            imp
            ))
        self.card.inputControl(
            uti.getValueOfConstantWithName(channel),
            coupling,
            uti.getValueOfConstantWithName(inputRange),
            imp
            )
        self.channels[channel] = True
        self._updateChannelCount()
        if not self.configureMode:
            self._runDependendConfiguration()

    def getMaxSamplesAndSampleSize(self):
        ''' no docstring '''
        return self.card.getChannelInfo()

    def getDataAtOnce(self, channel):
        '''
        :param channel: the channel whom the data belongs to
        :returns: all acquired data from one channel as one long list.
        '''
        if self.__class__ == BasicController:
            raise NotImplementedError(
                "No Acquisition is possible using the basic controller " +
                "and therefore there is no data!")
        data = []
        for record in self.data[channel]:
            data.extend(record)
        return data

    def getDataRecordWise(self, channel):
        """
        :param channel: the channel whom the data belongs to
        :returns: all acquired data from one channel as a list of
                  records.
        """
        if self.__class__ == BasicController:
            raise NotImplementedError(
                "No Acquisition is possible using the basic controller " +
                "and therefore there is no data!")
        return self.data[channel]

    def saveDataToTextFile(self, filename, channel):
        """
        saves the data of one channel to a textfile.

        Each line of the text file contains one record. The last line
        contains the time values for the samples in each record.
        """
        if self.__class__ == BasicController:
            raise NotImplementedError(
                "No Acquisition is possible using the basic controller " +
                "and therefore there is no data!")
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.savetxt(filename, data)

    def saveDataToNumpyFile(self, filename, channel):
        """
        saves the data of one channel to a numpy file.

        The records are arranged along the first axis of the array and
        the last element is the list of time values.
        """
        if self.__class__ == BasicController:
            raise NotImplementedError(
                "No Acquisition is possible using the basic controller " +
                "and therefore there is no data!")
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.save(filename, data)

    def startCapture(self):
        """starts measuring of the card."""
        if self.__class__ == BasicController:
            raise NotImplementedError("No Acquisition is possible using the basic controller!")
        else:
            if not self.readyForCapture:
                self._runDependendConfiguration()
        # Arm the board to wait for a trigger event to begin the acquisition
            if self.debugMode:
                print("startCapture")
            self.card.startCapture()

    def endCapture(self):
        """closes communication to card"""
        self.card.abortCapture()
        
    def getApproximateDuration(self):
        raise NotImplementedError(
            "As the BasicController cannot acquire data this function is not implemented.")

    def _setClock(self):
        """
        sets the sample rate on the card.
        """
        if self.debugMode:
            print("setCaptureClock")
            print("    sampleRate: {}".format(uti.getValueOfConstantWithName(self.sampleRate)))
        print("setCaptureClock(INTERNAL_CLOCK, {}, CLOCK_EDGE_RISING, 0)"
            .format(self.sampleRate))
        self.card.setCaptureClock(
            ats.INTERNAL_CLOCK,
            uti.getValueOfConstantWithName(self.sampleRate),
            ats.CLOCK_EDGE_RISING,
            0 # clock decimation
            )

    def _convertRawDataToInts(self, raw):
        """
        converts the data that is saved byte wise in little endian order
        to integers.
        """
        a_value = len(raw)
        shorts = unpack(str(a_value) + 'B', raw)
        a_value = len(shorts)
        return [(shorts[2 * i + 1] * 256 + shorts[2 * i]) // 4 for i in range(a_value // 2)]

    def _updateChannelCount(self):
        """
        counts the channels that are set true in self.channels and sets
        the corresponding variable.
        """
        self.channelCount = 0
        for key in self.channels.keys():
            if self.channels[key]:
                self.channelCount += 1

    def _runDependendConfiguration(self, startfunction=None):
        """
        runs all configuration functions in dependendFunctions starting
        with startfunction.

        Some functions that configure the controller or the card depend
        on each other meaning that the configuration done by one
        function can make it necessary to do the configuration by
        another function again. These functions are listed in
        dependendFunctions and the order is the order of their
        execution.

        :param startfunction: this is the first function that is
                              executed. All functions in
                              dependendFunctions that are before
                              this function are not executed.
        """
        start = 0
        if startfunction in self.dependendFunctions:
            start = self.dependendFunctions.index(startfunction)
        for function in self.dependendFunctions[start:]:
            function()

    def _getChannelMask(self):
        """
        creates the binary coded channel mask

        some Alazar functions need the channel mask as parameter.  This
        function creates it from the self.channels list.
        """
        channels = []
        for key in self.channels.keys():
            if self.channels[key]:
                channels.append(uti.getValueOfConstantWithName(key))
        if len(channels) == 0:
            return 0
        elif len(channels) == 1:
            return channels[0]
        else:
            mask = channels[0].value
            for channel in channels[1:]:
                mask = mask | channel.value
            return mask

    def _processData(self, data, channel):
        """converts the unsigned data to volts"""
        data = np.array(data, dtype='float')
        data -= 8192
        data *= self.inputRanges[channel] / 8192.
        return data


class AbstractTriggeredController(BasicController):
    """
    baseclass for all controller that use the trigger.
    """
    def __init__(self, **kwds):
        super(AbstractTriggeredController, self).__init__(**kwds)
        self.preTriggerSamples = 1024
        self.postTriggerSamples = 1024
        self.samplesPerRecord = self.preTriggerSamples + self.postTriggerSamples
        self.recordsPerCapture = 4

    def setSamplesPerRecord(self, samples=None, preTriggerSamples=None, postTriggerSamples=None):
        """
        sets the variables preTriggersamples, postTriggerSamples and
        samplesPerRecord.

        Supply either samples or both pre and postTriggerSamples.
        """
        if preTriggerSamples is None and postTriggerSamples is None and samples != None:
            self.preTriggerSamples = 0
            self.postTriggerSamples = int(samples)
            self.samplesPerRecord = int(samples)
        elif (preTriggerSamples != None and
              postTriggerSamples != None and
              samples is None):
            self.preTriggerSamples = int(preTriggerSamples)
            self.postTriggerSamples = int(postTriggerSamples)
            self.samplesPerRecord = int(preTriggerSamples + postTriggerSamples)
        else:
            raise Exception("supply either both or none pre/postTriggerSamples")
        if ((self.preTriggerSamples < 256 and self.preTriggerSamples != 0)
                or self.postTriggerSamples < 256):
            print("WARNING: When pre or postTriggerSamples are less " +
                  "than 256, some parts of the data might be scrambled.")
            print("preTriggerSamples = {}".format(preTriggerSamples))
            print("postTriggerSamples = {}".format(postTriggerSamples))
        if ((not uti.is_power2(self.preTriggerSamples) and
            self.preTriggerSamples != 0) or
            (not uti.is_power2(self.postTriggerSamples))):
            print("WARNING: Depending on your card the selected values " +
                  "for pre and/or postTriggeredSamples might lead to " +
                  "scrambled data. If possible choose values that are " +
                  "power of 2")
            print("preTriggerSamples = {}".format(preTriggerSamples))
            print("postTriggerSamples = {}".format(postTriggerSamples))

        if not self.configureMode:
            self._runDependendConfiguration()

    def getTimesOfRecord(self):
        """
        generates a time value to each sample value in a record.

        The time 0 is given to the first postTriggerSample. Time values
        are spaced according to the sampling rate.
        """
        sec = float(self.samplesPerRecord) / self.samplesPerSec
        return np.linspace(
            -sec * float(self.preTriggerSamples) / self.samplesPerRecord,
            sec * float(self.postTriggerSamples - 1) / self.samplesPerRecord,
            self.samplesPerRecord)

    def getTimesOfCapture(self):
        """
        generates a time value to each sample value in a capture.

        If the capture consists of multiple records, these time values
        are likely to be not the actual times of the measurement.  The
        first sample has the time 0. Time values are spaced according to
        the sampling rate.
        """
        return np.linspace(
            0.0,
            float(self.samplesPerRecord * self.recordsPerCapture - 1) / self.samplesPerSec,
            self.samplesPerRecord * float(self.recordsPerCapture))

    def setRecordsPerCapture(self, records):
        """
        sets the variable recordsPerCapture.
        """
        self.recordsPerCapture = records
        if not self.configureMode:
            self._runDependendConfiguration(self._setSizeOfCapture)

    def setCaptureDurationTo(self, seconds):
        """
        sets the number of records per capture according to the desired
        capture duration.
        """
        self.setRecordsPerCapture(
            int(ceil(float(seconds) / self.samplesPerRecord * self.samplesPerSec)))

    def setTrigger(
            self,
            operationType="TRIG_ENGINE_OP_J",
            sourceOfJ="TRIG_DISABLE",
            sourceOfK="TRIG_DISABLE",
            levelOfJ=128,
            levelOfK=128):
        """
        configures the trigger engines.

        :param operationType: string identifying the operation type
                              (default "TRIG_ENGINE_OP_J").

                              Possible strings are defined in the c
                              header file of the Alazar SDK.

                              Usually
                              /usr/local/AlazarTech/include/AlazarCmd.h
        :param sourceOfJ: string identifying the source of the signal
                          that shall create trigger events
                          (default "TRIG_DISABLE").

                          Possible strings are defined in the c header
                          file of the Alazar SDK.

                          Usually
                          /usr/local/AlazarTech/include/AlazarCmd.h
        :param sourceOfK: string identifying the source of the signal
                          that shall create trigger events
                          (default "TRIG_DISABLE").

                          Possible strings are defined in the c header
                          file of the Alazar SDK.

                          Usually
                          /usr/local/AlazarTech/include/AlazarCmd.h
        :param levelOfJ: the voltage level that triggers. Must be an
                         integer between 0 (-range) and 255 (+range)
                         indicating the fraction of the input range
        :param levelOfK: the voltage level that triggers. Must be an
                         integer between 0 (-range) and 255 (+range)
                         indicating the fraction of the input range
        """

        # disable delay
        trigger_delay_samples = 0
        if self.debugMode:
            print("setTriggerDelay")
            print("    delay: {}".format(trigger_delay_samples))
        self.card.setTriggerDelay(trigger_delay_samples)
        # configure trigger
        if operationType not in uti.getNamesOfConstantsThatStartWith("TRIG_ENGINE_OP_"):
            raise Exception("Undefined operation type in createInput")
        if (sourceOfJ not in uti.getNamesOfConstantsThatStartWith("TRIG_"))\
        or (sourceOfJ in uti.getNamesOfConstantsThatStartWith("TRIG_ENGINE_")):
            raise Exception("Wrong source for trigger engine J")
        if (sourceOfK not in uti.getNamesOfConstantsThatStartWith("TRIG_"))\
        or (sourceOfK in uti.getNamesOfConstantsThatStartWith("TRIG_ENGINE_")):
            raise Exception("Wrong source for trigger engine K")
        if levelOfJ not in range(256):
            raise Exception("Wrong level for trigger engine J")
        if levelOfK not in range(256):
            raise Exception("Wrong level for trigger engine K")

        op_cons = uti.getValueOfConstantWithName(operationType)
        if self.debugMode:
            print("setTriggerOperation")
            print("    operationType: {}".format(op_cons))
        print("setTriggerOperation({}, TRIG_ENGINE_J, {}, TRIGGER_SLOPE_POSITIVE, {}, TRIG_ENGINE_K, {}, TRIGGER_SLOPE_POSITIVE, {})".format(
            op_cons,
            sourceOfJ,
            levelOfJ,
            sourceOfK,
            levelOfK
            ))
        self.card.setTriggerOperation(
            op_cons,
            ats.TRIG_ENGINE_J,
            uti.getValueOfConstantWithName(sourceOfJ),
            ats.TRIGGER_SLOPE_POSITIVE,
            levelOfJ,
            ats.TRIG_ENGINE_K,
            uti.getValueOfConstantWithName(sourceOfK),
            ats.TRIGGER_SLOPE_POSITIVE,
            levelOfK
            )

    def setTriggerTimeout(self, triggerTimeout_sec=0.):
        """configures the timeout of the trigger.

        If no trigger event is created by the trigger engines within the
        trigger timeout, a trigger event is created after the trigger
        timeout time. A timeout of 0 means that no trigger event is ever
        created because of a timeout.

        :param triggerTimeout_sec: the trigger timeout in seconds
                                   (default 0.0).
        """
        self.triggerTimeout = triggerTimeout_sec
        triggerTimeout_clocks = c_uint32(int(triggerTimeout_sec / 10e-6 + 0.5))
        if self.debugMode:
            print("setTriggerTimeOut")
            print("    triggerTimeout_clocks: {}".format(triggerTimeout_clocks))
        self.card.setTriggerTimeOut(triggerTimeout_clocks)

class AbstractADMAController(BasicController):
    """
    baseclass for all controller that use ADMA.
    """
    def __init__(self, **kwds):
        super(AbstractADMAController, self).__init__(**kwds)
        self.number_of_buffers = 4
        self.recordsPerBuffer = 1
        self.buffers_per_capture = 4
        self.data_buffers = []

    def readData(self, timeOut=None):
        """
        read all acquired data from the card memory.

        The data is returned in a dictionary. The keys are the
        respective channel names.

        :param timeOut: a time out in ms. If the capture is not
                        finished within the time out, it is aborted.
                        default is 100 s.
        """
        buffer_index = 0
        if timeOut is None:
            timeOut = int(1e6)
        for _ in range(self.buffers_per_capture):
            self.card.waitAsyncBufferComplete(
                self.data_buffers[buffer_index],
                timeOut
                )

            # cast the void pointer to the appropriet ctypes c_char_array type
            self._processBuffer((c_char * self.bytes_per_buffer)
                                .from_address(int(self.data_buffers[buffer_index].value)).raw)

            self.card.postAsyncBuffer(
                self.data_buffers[buffer_index],
                self.bytes_per_buffer
                )

            buffer_index += 1
            buffer_index %= self.number_of_buffers

        self.card.abortAsyncRead()
        self.readyForCapture = False

    def setNumberOfBuffers(self, buffers):
        self.number_of_buffers = buffers

        if not self.configureMode:
            self._runDependendConfiguration(self._setSizeOfCapture)

    def _getPreTriggerSamples(self):
        """
        acquires a value for an Alazar function.
        """
        raise NotImplementedError()

    def _getSamplesPerRecord(self):
        """
        acquires a value for an Alazar function.
        """
        raise NotImplementedError()

    def _getRecordsPerBuffer(self):
        """
        acquires a value for an Alazar function.
        """
        raise NotImplementedError()

    def _getRecordsPerCapture(self):
        """
        acquires a value for an Alazar function.
        """
        raise NotImplementedError()

    def _createPageAlignedBuffer(self, buffersize):
        """Return a pointer to a page-aligned buffer.

        The pointer should be freed with libc.free() when finished"""

        # Need to align to a page boundary, so use valloc
        addr = self.libc.valloc(buffersize)
        addr = c_void_p(addr)

        if addr == 0:
            raise Exception("Failed to allocate memory")
        return addr

    def _prepareCapture(self):
        """
        has to be called before the capture can be started.
        """
        self.card.abortAsyncRead()
        self.readyForCapture = False

        if self.channelCount == 3:
            raise AlazarCardError("The card does not allow the acquisition " +
                                  "on three channels. Use four instead.")


        if self.debugMode:
            print("beforeAsyncRead\n")
        self.card.beforeAsyncRead(
            self._getChannelMask(),
            - self._getPreTriggerSamples(),
            self._getSamplesPerRecord(),
            self._getRecordsPerBuffer(),
            self._getRecordsPerCapture(),
            self.adma_flags
            )

        self.data = {}
        for channel in self.channels.keys():
            if self.channels[channel]:
                self.data[channel] = []

        self.data_buffers = []
        for index in range(self.number_of_buffers):
            self.data_buffers.append(self._createPageAlignedBuffer(self.bytes_per_buffer))
            self.card.postAsyncBuffer(
                self.data_buffers[index],
                self.bytes_per_buffer
                )

        self.readyForCapture = True


class AbstractTriggeredADMAController(AbstractTriggeredController, AbstractADMAController):
    """
    baseclass for controllers that use ADMA and are triggered.
    """
    def __init__(self, **kwds):
        super(AbstractTriggeredADMAController, self).__init__(**kwds)
        self.configureMode = True
        self.setRecordsPerCapture(self.recordsPerCapture)
        self.configureMode = False

    def setRecordsPerCapture(self, records):
        """
        set the number or records per capture.

        This function has to be reimplemented as it interferes with the
        setting of recordsPerBuffer and buffers_per_capture.
        """

        recsPerBuf = 1 #only one record/buffer allowed in triggered mode
        bufsPerCapt = int(records)

        self.setRecordsPerBuffer(recsPerBuf, bufsPerCapt)

    def setRecordsPerBuffer(self, recsPerBuf, bufsPerCapt):
        """
        sets recordsPerBuffer and buffers_per_capture
        """
        self.recordsPerBuffer = recsPerBuf
        self.buffers_per_capture = bufsPerCapt
        self.recordsPerCapture = self.recordsPerBuffer * self.buffers_per_capture
        if not self.configureMode:
            self._runDependendConfiguration(self._setSizeOfCapture)


class ContinuousController(AbstractADMAController):
    """
    This controller shall be used when data has to be acquired
    continuously.

    In the simplest scenario use the controller like this:
        control = ContinuousController()
        control.createInput()
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setCaptureDurationTo(1)
        control.startCapture()
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
        # set variables for dependend functions
        self.dependendFunctions = [self._setClock, self._setSizeOfCapture, self._prepareCapture]
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
            self._runDependendConfiguration(self._setSizeOfCapture)

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
        return np.linspace(
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
            self._runDependendConfiguration(self._setSizeOfCapture)

    def _getPreTriggerSamples(self):
        return 0

    def _getSamplesPerRecord(self):
        return self.samples_per_buffer

    def _getRecordsPerBuffer(self):
        return 1

    def _getRecordsPerCapture(self):
        return self.buffers_per_capture

    def _processBuffer(self, data):
        data = self._convertRawDataToInts(data)
        for i, channel in enumerate(sorted(self.data.keys())):
            self.data[channel].append(list(
                self._processData(data[i * self.samples_per_buffer:(i + 1) *
                self.samples_per_buffer], channel)))

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
        self.bytes_per_sample = int(ceil(bits_per_sample / 8.0))
        self.bytes_per_buffer = int(self.bytes_per_sample * self.samples_per_buffer * self.channelCount)


class TriggeredContinuousController(AbstractTriggeredADMAController):
    """
    This controller shall be used when data has to be acquired after
    trigger events.

    In the simplest scenario use the controller like this:
        control = TriggeredContinuousController()
        control.createInput()
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.startCapture()
        control.readData()
        data = control.getDataAtOnce("CHANNEL_A")

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
        self.dependendFunctions = [self._setClock, self._setSizeOfCapture, self._prepareCapture]
        self.preTriggerSamples = 0
        self.samplesPerRecord = self.postTriggerSamples
        self.adma_flags = 0x1 | 0x200
        self.bytes_per_sample = 0
        self.bytes_per_buffer = 0

    def setSamplesPerRecord(self, samples=None, preTriggerSamples=None, postTriggerSamples=None):
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
            float(self.samplesPerRecord) *
            self.recordsPerBuffer * self.buffers_per_capture / self.samplesPerSec)

    def _getPreTriggerSamples(self):
        return self.preTriggerSamples

    def _getSamplesPerRecord(self):
        return self.samplesPerRecord

    def _getRecordsPerBuffer(self):
        return self.recordsPerBuffer

    def _getRecordsPerCapture(self):
        return self.buffers_per_capture * self.recordsPerBuffer

    def _processBuffer(self, data):
        data = self._convertRawDataToInts(data)
        records = [data[i * self.samplesPerRecord:(i + 1) * self.samplesPerRecord] for i in range(
            self.recordsPerBuffer * self.channelCount)]
        for i, channel in enumerate(sorted(self.data.keys())):
            for record in records[i * self.recordsPerBuffer:(i + 1) * self.recordsPerBuffer]:
                print('self.data', self.data)
                self.data[channel].append(list(self._processData(record, channel)))

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
        self.bytes_per_sample = int(ceil(bits_per_sample / 8.0))

        self.bytes_per_buffer = int(
            self.bytes_per_sample
            * self.recordsPerBuffer
            * self.samplesPerRecord
            * self.channelCount)

        if self.debugMode:
            print("setRecordSize")
            print("    preTriggerSamples: {}".format(self.preTriggerSamples))
            print("    postTriggerSamples: {}".format(self.postTriggerSamples))
        self.card.setRecordSize(
                self.preTriggerSamples,
                self.postTriggerSamples
                )


class TriggeredRecordingController(AbstractTriggeredADMAController):
    """
    This controller shall be used when data has to be acquired at
    trigger events.

    In the simplest scenario use the controller like this:
        control = TriggeredRecordingController()
        control.createInput()
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.startCapture()
        control.readData()
        data = control.getDataAtOnce("CHANNEL_A")

    The card will record on Channel A with a sample rate of 100,000
    samples per second and trigger when 0 V is crossed with positive
    slope. The trigger events are assumed to be within 0.1 s. If there
    is no trigger event within this time a trigger event will be
    generated automatically. The data is structured in records where
    each record belongs to one trigger event. The returned data is one
    continuous list of samples.

    This controller does allow preTriggerSamples (although there are
    restrictions, see setSamplesPerRecord).
    """
    def __init__(self, **kwds):
        super(TriggeredRecordingController, self).__init__(**kwds)
        # set variables for dependend functions
        self.dependendFunctions = [self._setClock, self._setSizeOfCapture, self._prepareCapture]
        self.adma_flags = 0x1 | 0x0
        self.bytes_per_buffer = 0
        self.bytes_per_sample = 0

    def getApproximateDuration(self):
        return  int(float(self.samplesPerRecord) * self.recordsPerCapture / self.samplesPerSec)

    def _getPreTriggerSamples(self):
        return self.preTriggerSamples

    def _getSamplesPerRecord(self):
        return self.samplesPerRecord

    def _getRecordsPerBuffer(self):
        return self.recordsPerBuffer

    def _getRecordsPerCapture(self):
        return self.recordsPerBuffer * self.buffers_per_capture

    def _processBuffer(self, data):
        data = self._convertRawDataToInts(data)
        records = [data[i * self.samplesPerRecord:(i + 1) * self.samplesPerRecord] for i in range(
            self.recordsPerBuffer * self.channelCount)]
        for i, channel in enumerate(sorted(self.data.keys())):
            for record in records[i::self.channelCount]:
                self.data[channel].append(list(self._processData(record, channel)))


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
        self.bytes_per_sample = int(ceil(bits_per_sample.value / 8.))

        self.bytes_per_buffer = int(
            self.bytes_per_sample
            * self.recordsPerBuffer
            * self.samplesPerRecord
            * self.channelCount)

        while self.bytes_per_buffer > 16e6:
            self.recordsPerBuffer += 1
            self.bytes_per_buffer = int(
                self.bytes_per_sample
                * self.recordsPerBuffer
                * self.samplesPerRecord
                * self.channelCount)

        if self.debugMode:
            print("setRecordSize")
            print("    preTriggerSamples: {}".format(self.preTriggerSamples))
            print("    postTriggerSamples: {}".format(self.postTriggerSamples))
        self.card.setRecordSize(
            self.preTriggerSamples,
            self.postTriggerSamples
            )


class TriggeredRecordingSingleModeController(AbstractTriggeredController):
    """
    This controller saves the acquired data first on the card memory and
    transfers it to the program when the acquisition is finished.

    *DO NOT USE* this controller if not necessary. Probably,
    TriggeredRecordingController is a good alternative.
    """
    def __init__(self, **kwds):
        super(TriggeredRecordingSingleModeController, self).__init__(**kwds)
        self.dependendFunctions = [self._setClock, self._setSizeOfCapture]
        self.recordsPerCapture = 5
        print("It is strongly recommended to use the DualMode controllers. " +
              "This controller sometimes delivers wrong data (all prior " +
              "observations showed that the bad data is at the lower limit of " +
              "the input range).")
        self.bytes_per_sample = 0
        self.bytes_per_buffer = 0

    def readData(self, channel):
        if self.card.busy():
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
                    if self.debugMode:
                        print("read:\n\tchannel: ", uti.getValueOfConstantWithName(channel), \
                        "\n\tdata_buffer: ", data_buffer, \
                        "\n\tbytesPerSample: ", self.bytes_per_sample, \
                        "\n\trecord: ", record + 1, \
                        "\n\tpre: ", -self.preTriggerSamples, \
                        "\n\tsamples: ", self.samplesPerRecord)
                    self.card.read(
                        uti.getValueOfConstantWithName(channel),
                        data_buffer,
                        self.bytes_per_sample,
                        record + 1,
                        - (self.preTriggerSamples),
                        self.samplesPerRecord
                        )
                    self.data[channel].append(self._convertRawDataToInts(data_buffer.raw)[:-16])
        for channel in self.data.keys():
            self.data[channel] = self._processData(self.data[channel], channel)

    def waitForEndOfCapture(self, updateInterval=0.1):
        while self.card.busy():
            if updateInterval > 0:
                print("busy")
                sleep(updateInterval)
            else:
                sleep(-updateInterval)

    def setRecordsPerCapture(self, recordsPerCapture):
        self.recordsPerCapture = recordsPerCapture
        if not self.configureMode:
            self._runDependendConfiguration(self._setSizeOfCapture)

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

        if self.debugMode:
            print("setRecordSize")
            print("    preTriggerSamples: {}".format(self.preTriggerSamples))
            print("    postTriggerSamples: {}".format(self.postTriggerSamples))
        self.card.setRecordSize(
            self.preTriggerSamples,
            self.postTriggerSamples
            )

        if self.debugMode:
            print("setRecordCount:\n\trecordsPerCapture: ", self.recordsPerCapture)
        self.card.setRecordCount(self.recordsPerCapture)

        self.readyForCapture = True
