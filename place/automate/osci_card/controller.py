"""This module allows the data acquisition with an Alazar oscilloscope card.

Update
-----------
Significant changes have been made to this file. These changes have
been made to link it to the Alazar Python wrappers supplied by Alazar.
In many ways, this file should be considered obsolete, although efforts
were made to maintain its functionality. Documentation beyond this point
may be outdated, but will be corrected as encountered. ~Paul (24/01/2017)

Quick Info
-----------

There are four different controllers available:

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
therefore be used by just using the functions that DO not begin with an
underscore.

Remarks

Some configurations depend on each other. E.g. setting the number of
samples by defining the duration of the capture is not possible as long
as the sample rate is not set. Therefore, each controller has a
dependent_functions list. When a function is called on which other
functions depend the functions in this list are executed in a defined
order. The exception to this rule is when the configureMode variable is
true. In this case the configuration is done only within this program
without telling the card. If start_capture realizes that the
configuration is not finished it triggers the execution of the
dependent_functions.

@author: Henrik tom Woerden
Created on Jun 27, 2013
"""
from __future__ import print_function

import json
from ctypes import cdll, c_uint32, c_char, c_void_p
from math import ceil
from warnings import warn

import numpy as np

from place.alazartech import atsapi as ats

from .utility import (
    get_sample_rate_from,
    getValueOfConstantWithName,
    getNamesOfConstantsThatStartWith,
    convert_raw_data_to_ints,
    get_input_range_from,
    is_power2,
    )

ATS_SUCCESS = 512
ADMA_EXTERNAL_STARTCAPTURE = 0x1

class BasicController(ats.Board):
    """Provides basic functionality to communicate with an Alazar card.

    This class is not intended for real usage; at most for testing. It
    is the base class of all more sophisticated controllers. Functions

    that are common in all controllers are defined in this class; some
    of them do nothing but raise an NotImplementedError Exception.
    """
    libc = cdll.LoadLibrary('libc.so.6')

    def __init__(self, opts=None, system_id=1, board_id=1):
        """Constructor

        From the ATS-SDK-Guide...
            "Before acquiring data from a board system, an application must
            configure the timebase, analog inputs, and trigger system settings
            for each board in the board system."

        :param opts: dictionary of options for the oscilloscope card
        :type opts: dict

        :param system_id: system to address
        :type system_id: int

        :param board_id: board to address
        :type board_id: int
        """
        super(BasicController, self).__init__(system_id, board_id)
        self.par = {}
        if opts:
            self.par = opts
            self._config_timebase()
            self._config_analog_inputs()
            self._config_trigger_system()
        else:
            warn('opts not passed to controller')
        self.input_ranges = {}
        self.configureMode = False
        self.sampleRate = "SAMPLE_RATE_1MSPS"
        self.dependent_functions = []
        self.readyForCapture = False
        self.channelCount = 0
        self.data = {}
        self.channelsPerBoard = 4
        self.channels = {
            "CHANNEL_A":False,
            "CHANNEL_B":False,
            "CHANNEL_C":False,
            "CHANNEL_D":False
            }
        self.samplesPerSec = 0

    def _config_timebase(self):
        """Sets the capture clock"""
        self.setCaptureClock(
            getattr(ats, self.par['clock_source']),
            getattr(ats, self.par['sample_rate']),
            getattr(ats, self.par['clock_edge']),
            self.par['decimation']
            )

    def _config_analog_inputs(self):
        """Specify the desired input range, termination, and coupling of and
        input channel
        """
        for config in self.par['analog_inputs']:
            self.inputControl(
                getattr(ats, config['input_channel']),
                getattr(ats, config['input_coupling']),
                getattr(ats, config['input_range']),
                getattr(ats, config['input_impedance'])
                )

    def _config_trigger_system(self):
        """Configure each of the two trigger engines"""
        self.setTriggerOperation(
            getattr(self.par['trigger_operation']),
            getattr(self.par['trigger_engine_1']),
            getattr(self.par['source_1']),
            getattr(self.par['slope_1']),
            getattr(self.par['level_1']),
            getattr(self.par['trigger_engine_2']),
            getattr(self.par['source_2']),
            getattr(self.par['slope_2']),
            getattr(self.par['level_2']),
            )

    def setSampleRate(self, sampleRate):
        """Sets variables that belong to the sample rate."""
        self.sampleRate = sampleRate
        self.samplesPerSec = get_sample_rate_from(self.sampleRate)
        if not self.configureMode:
            self._run_dependent_configuration(self._setClock)

    def create_input(
            self,
            channel=ats.CHANNEL_A,
            input_range=ats.INPUT_RANGE_PM_400_MV,
            coupling=ats.DC_COUPLING,
            impedance=ats.IMPEDANCE_50_OHM):
        """Configures one channel for measurement.

        :param channel: the channel to use

        :param input_ranges: the input range

        :param coupling: AC or DC coupling

        :param impedance: the impedance of the channel in ohms
        """
        # support the old style of passing stuff
        if isinstance(channel, str):
            warn("channel passed as string - consider using ATS constant instead")
            channel = getattr(ats, channel)
        if isinstance(input_range, str):
            warn("input range passed as string - consider using ATS constant instead")
            input_range = getattr(ats, input_range)
        if isinstance(coupling, str):
            warn("coupling passed as string - consider using ATS constant instead")
            coupling = getattr(ats, coupling)
        elif isinstance(coupling, bool):
            warn("coupling passed as boolean - consider using ATS constant instead")
            if coupling is True:
                coupling = ats.AC_COUPLING
            else:
                coupling = ats.DC_COUPLING
        if isinstance(impedance, str):
            warn("impedance passed as string - consider using ATS constant instead")
            impedance = getattr(ats, impedance)

        self.input_ranges[channel] = get_input_range_from(input_range)
        self.channels[channel] = True

        self.inputControl(channel, coupling, input_range, impedance)

        self.channelCount = 0
        for channel in self.channels.values():
            if channel:
                self.channelCount += 1
        if not self.configureMode:
            self._run_dependent_configuration()

    def getMaxSamplesAndSampleSize(self):
        return self.getChannelInfo()

    def getDataAtOnce(self, channel):
        """Get data

        :param channel: the channel whom the data belongs to
        :returns: all acquired data from one channel as one long list.
        """
        raise NotImplementedError(
            "No Acquisition is possible using the basic controller " +
            "and therefore there is no data!")

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
        raise NotImplementedError(
            "No Acquisition is possible using the basic controller " +
            "and therefore there is no data!")

    def saveDataToNumpyFile(self, filename, channel):
        """
        saves the data of one channel to a numpy file.

        The records are arranged along the first axis of the array and
        the last element is the list of time values.
        """
        raise NotImplementedError(
            "No Acquisition is possible using the basic controller " +
            "and therefore there is no data!")

    def start_capture(self):
        """starts measuring of the card."""
        raise NotImplementedError(
            "No Acquisition is possible using the basic controller!")

    def endCapture(self):
        """closes communication to card"""
        self.abortCapture()

    def getApproximateDuration(self):
        """ interface method to be implemented by sub-classes """
        raise NotImplementedError

    def _setClock(self):
        """
        sets the sample rate on the card.
        """
        clock_decimation = 0
        if isinstance(self.sampleRate, str):
            warn('setCaptureClock() was given sampleRate as a string')
            self.sampleRate = getValueOfConstantWithName(self.sampleRate)
        self.setCaptureClock(
            ats.INTERNAL_CLOCK,
            self.sampleRate,
            ats.CLOCK_EDGE_RISING,
            clock_decimation
            )

    def _run_dependent_configuration(self, startfunction=None):
        """
        runs all configuration functions in dependent_functions starting
        with startfunction.

        Some functions that configure the controller or the card depend
        on each other meaning that the configuration done by one
        function can make it necessary to do the configuration by
        another function again. These functions are listed in
        dependent_functions and the order is the order of their
        execution.

        :param startfunction: this is the first function that is
                              executed. All functions in
                              dependent_functions that are before
                              this function are not executed.
        """
        start = 0
        if startfunction in self.dependent_functions:
            start = self.dependent_functions.index(startfunction)
        for function in self.dependent_functions[start:]:
            function()

    def _get_channel_mask(self):
        """creates the binary coded channel mask

        some Alazar functions need the channel mask as parameter.  This
        function creates it from the self.channels list.
        """
        channels = []
        for key, value in self.channels.items():
            if value:
                channels.append(key)
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
        data *= self.input_ranges[channel] / 8192.
        return data


class AbstractTriggeredController(BasicController):
    """baseclass for all controller that use the trigger."""
    def __init__(self, **kwds):
        super(AbstractTriggeredController, self).__init__(**kwds)
        self.preTriggerSamples = 1024
        self.postTriggerSamples = 1024
        self.samplesPerRecord = self.preTriggerSamples + self.postTriggerSamples
        self.recordsPerCapture = 4

    def _setSizeOfCapture(self):
        raise NotImplementedError

    def set_record_size(self):
        """Pass the subclass data to the superclass method"""
        self.setRecordSize(self.preTriggerSamples, self.postTriggerSamples)

    def saveDataToTextFile(self, filename, channel):
        """saves the data of one channel to a textfile.

        Each line of the text file contains one record. The last line
        contains the time values for the samples in each record.
        """
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.savetxt(filename, data)

    def saveDataToNumpyFile(self, filename, channel):
        """Saves the data of one channel to a numpy file.

        The records are arranged along the first axis of the array and
        the last element is the list of time values.
        """
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.save(filename, data)

    def start_capture(self):
        """starts measuring of the card."""
        if not self.readyForCapture:
            self._run_dependent_configuration()
        self.startCapture()

    def getDataAtOnce(self, channel):
        """
        :param channel: the channel whom the data belongs to
        :returns: all acquired data from one channel as one long list.
        """
        data = []
        for record in self.data[channel]:
            data.extend(record)
        return data

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
        if ((not is_power2(self.preTriggerSamples) and
             self.preTriggerSamples != 0) or
                (not is_power2(self.postTriggerSamples))):
            print("WARNING: Depending on your card the selected values " +
                  "for pre and/or postTriggeredSamples might lead to " +
                  "scrambled data. If possible choose values that are " +
                  "power of 2")
            print("preTriggerSamples = {}".format(preTriggerSamples))
            print("postTriggerSamples = {}".format(postTriggerSamples))

        if not self.configureMode:
            self._run_dependent_configuration()

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
            self._run_dependent_configuration(self._setSizeOfCapture)

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
        self.setTriggerDelay(trigger_delay_samples)
        # configure trigger
        if operationType not in getNamesOfConstantsThatStartWith("TRIG_ENGINE_OP_"):
            raise Exception("Undefined operation type in create_input")
        if (sourceOfJ not in getNamesOfConstantsThatStartWith("TRIG_"))\
        or (sourceOfJ in getNamesOfConstantsThatStartWith("TRIG_ENGINE_")):
            raise Exception("Wrong source for trigger engine J")
        if (sourceOfK not in getNamesOfConstantsThatStartWith("TRIG_"))\
        or (sourceOfK in getNamesOfConstantsThatStartWith("TRIG_ENGINE_")):
            raise Exception("Wrong source for trigger engine K")
        if levelOfJ not in range(256):
            raise Exception("Wrong level for trigger engine J")
        if levelOfK not in range(256):
            raise Exception("Wrong level for trigger engine K")

        op_cons = getValueOfConstantWithName(operationType)
        print("setTriggerOperation({}, TRIG_ENGINE_J, {}, TRIGGER_SLOPE_POSITIVE, {}, TRIG_ENGINE_K, {}, TRIGGER_SLOPE_POSITIVE, {})".format(
            op_cons,
            sourceOfJ,
            levelOfJ,
            sourceOfK,
            levelOfK
            ))
        self.setTriggerOperation(
            op_cons,
            ats.TRIG_ENGINE_J,
            getValueOfConstantWithName(sourceOfJ),
            ats.TRIGGER_SLOPE_POSITIVE,
            levelOfJ,
            ats.TRIG_ENGINE_K,
            getValueOfConstantWithName(sourceOfK),
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
        self.setTriggerTimeOut(triggerTimeout_clocks)

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
        self.adma_flags = ADMA_EXTERNAL_STARTCAPTURE
        self.bytes_per_buffer = None

    def _setSizeOfCapture(self):
        raise NotImplementedError

    def getTimesOfRecord(self):
        raise NotImplementedError

    def saveDataToTextFile(self, filename, channel):
        """saves the data of one channel to a textfile.

        Each line of the text file contains one record. The last line
        contains the time values for the samples in each record.
        """
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.savetxt(filename, data)

    def saveDataToNumpyFile(self, filename, channel):
        """saves the data of one channel to a numpy file.

        The records are arranged along the first axis of the array and
        the last element is the list of time values.
        """
        data = np.array(self.data[channel])
        times = self.getTimesOfRecord()
        data = np.vstack((data, times))
        np.save(filename, data)

    def getDataAtOnce(self, channel):
        """Get data

        :param channel: the channel whom the data belongs to
        :returns: all acquired data from one channel as one long list.
        """
        data = []
        for record in self.data[channel]:
            data.extend(record)
        return data

    def start_capture(self):
        """starts measuring of the card."""
        if not self.readyForCapture:
            self._run_dependent_configuration()
        self.startCapture()

    def _processBuffer(self, data):
        raise NotImplementedError

    def readData(self, timeOut=None):
        """read all acquired data from the card memory.

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
            self.waitAsyncBufferComplete(
                self.data_buffers[buffer_index],
                timeOut
                )

            # cast the void pointer to the appropriet ctypes c_char_array type
            self._processBuffer((c_char * self.bytes_per_buffer)
                                .from_address(int(self.data_buffers[buffer_index].value)).raw)

            self.postAsyncBuffer(
                self.data_buffers[buffer_index],
                self.bytes_per_buffer
                )

            buffer_index += 1
            buffer_index %= self.number_of_buffers

        self.abortAsyncRead()
        self.readyForCapture = False

    def setNumberOfBuffers(self, buffers):
        self.number_of_buffers = buffers

        if not self.configureMode:
            self._run_dependent_configuration(self._setSizeOfCapture)

    def _getPreTriggerSamples(self):
        """acquires a value for an Alazar function."""
        raise NotImplementedError()

    def _getSamplesPerRecord(self):
        """acquires a value for an Alazar function."""
        raise NotImplementedError()

    def _getRecordsPerBuffer(self):
        """acquires a value for an Alazar function."""
        raise NotImplementedError()

    def _getRecordsPerCapture(self):
        """acquires a value for an Alazar function."""
        raise NotImplementedError()

    def _createPageAlignedBuffer(self, buffersize):
        """Return a pointer to a page-aligned buffer.

        The pointer should be freed with libc.free() when finished"""

        # Need to align to a page boundary, so use valloc
        addr = BasicController().libc.valloc(buffersize)
        addr = c_void_p(addr)

        if addr == 0:
            raise Exception("Failed to allocate memory")
        return addr

    def _prepare_capture(self):
        """has to be called before the capture can be started."""
        self.abortAsyncRead()
        self.readyForCapture = False
        
        try:
            self.beforeAsyncRead(
                self._get_channel_mask(),
                (- self._getPreTriggerSamples()),
                self._getSamplesPerRecord(),
                self._getRecordsPerBuffer(),
                self._getRecordsPerCapture(),
                self.adma_flags
                )
        except Exception as err: #pylint: disable=broad-except
            message = str(err)
            if 'ApiUnsupportedFunction' in message:
                raise RuntimeError('This device does not support asynchronous ADMA')
            else:
                raise err

        self.data = {}
        for channel in self.channels:
            if self.channels[channel]:
                self.data[channel] = []

        self.data_buffers = []
        for index in range(self.number_of_buffers):
            self.data_buffers.append(self._createPageAlignedBuffer(self.bytes_per_buffer))
            self.postAsyncBuffer(
                self.data_buffers[index],
                self.bytes_per_buffer
                )

        self.readyForCapture = True

class AbstractTriggeredADMAController(AbstractTriggeredController, AbstractADMAController):
    """baseclass for controllers that use ADMA and are triggered."""
    def __init__(self, **kwds):
        super(AbstractTriggeredADMAController, self).__init__(**kwds)
        self.configureMode = True
        self.setRecordsPerCapture(self.recordsPerCapture)
        self.configureMode = False
        self.bytes_per_sample = 0

    def setRecordsPerCapture(self, records):
        """
        set the number or records per capture.

        This function has to be reimplemented as it interferes with the
        setting of recordsPerBuffer and buffers_per_capture.
        """

        records_per_buffer = 1 #only one record/buffer allowed in triggered mode
        buffers_per_capture = int(records)

        self.setRecordsPerBuffer(records_per_buffer, buffers_per_capture)

    def setRecordsPerBuffer(self, records_per_buffer, buffers_per_capture):
        """
        sets recordsPerBuffer and buffers_per_capture
        """
        self.recordsPerBuffer = records_per_buffer
        self.buffers_per_capture = buffers_per_capture
        self.recordsPerCapture = self.recordsPerBuffer * self.buffers_per_capture
        if not self.configureMode:
            self._run_dependent_configuration(self._setSizeOfCapture)

    def _getPreTriggerSamples(self):
        return self.preTriggerSamples

    def _getSamplesPerRecord(self):
        return self.samplesPerRecord

    def _getRecordsPerBuffer(self):
        return self.recordsPerBuffer

    def _getRecordsPerCapture(self):
        return self.recordsPerBuffer * self.buffers_per_capture

    def _calc_bytes_per_buffer(self):
        """Compute the bytes_per_buffer value"""
        self.bytes_per_buffer = int(
            self.bytes_per_sample
            * self.recordsPerBuffer
            * self.samplesPerRecord
            * self.channelCount
            )
        return self.bytes_per_buffer

    def _processBuffer(self, data):
        data = convert_raw_data_to_ints(data)
        samples = self.samplesPerRecord
        count = self.recordsPerBuffer * self.channelCount
        records = [data[i * samples:(i + 1) * samples] for i in range(count)]
        for i, channel in enumerate(sorted(self.data)):
            start = i * self.recordsPerBuffer
            stop = start + self.recordsPerBuffer
            for record in records[start:stop]:
                print('self.data', self.data)
                self.data[channel].append(list(self._processData(record, channel)))

    def _setSizeOfCapture(self):
        """Defines the length of a record in samples."""
        raise NotImplementedError()
