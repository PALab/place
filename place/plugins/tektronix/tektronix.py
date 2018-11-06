"""Tektronix oscilloscope."""

from socket import AF_INET, SOCK_STREAM, socket
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

from place.config import PlaceConfig
from place.plots import DEFAULT_DPI, DEFAULT_FIGSIZE
from place.plugins.instrument import Instrument


class TektronixCommon(Instrument):
    #pylint: disable=too-many-instance-attributes
    """Common class for all Tektronix oscilloscopes.

    The Tektronix oscilloscope requires the following configuration data
    (accessible as self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    force_trigger             bool           ``True`` if oscilloscope should automatically
                                             trigger. ``False`` if oscilloscope should wait
                                             for trigger.
    plot                      bool           ``True`` if plotting should occur, otherwise
                                             ``False``.
    ========================= ============== ================================================

    The oscilloscope will produce the following experimental metadata:

    =========================== ============== ==============================================
    Key                         Type           Meaning
    =========================== ============== ==============================================
    *model*-active_channels     list           This is a list of boolean values to indicate
                                               which channels were active on the
                                               oscilloscope when the trace was acquired.
    *model*-sample_rate         float          The sample rate, as reported by the
                                               oscilloscope.
    *model*-record_length       int            The horizontal record length, as reported by
                                               the oscilloscope.
    *model*-chN_x_zero          float          The zero point of the x-axis for channel
                                               *N*, as reported by the oscilloscope.
    *model*-chN_x_increment     float          The increment between data point for channel
                                               *N*, as reported by the oscilloscope.
    *model*-chN_y_zero          float          The zero point of the y-axis for channel
                                               *N*, as reported by the oscilloscope.
    *model*-chN_y_offset        float          The offset of the y-axis data for channel
                                               *N*, as reported by the oscilloscope.
    *model*-chN_y_multiplier    float          The multiplier for the y-axis data for
                                               channel *N*, as reported by the oscilloscope.
    =========================== ============== ==============================================

    You can use the following equation to compute the voltage:

    .. code-block:: python

        volts = (trace - y_offset) * y_multiplier + y_zero
        time = (np.linspace(0, x_increment * len(volts), len(volts)) + x_zero)

    This module will produce the following experimental data:

    +---------------+-------------------------+-------------------------+
    | Heading       | Type                    | Meaning                 |
    +===============+=========================+=========================+
    | *model*-trace | [channel X sample]      | the trace data recorded |
    |               | array of uint16         | on the oscilloscope     |
    +---------------+-------------------------+-------------------------+

    .. note::

        In the output data, *model* will be replaced by the model number of the
        oscilloscope in use (i.e. DPO3014).

    """
    _bytes_per_sample = 2
    # (<)little-endian, (i)signed integer
    _data_type = np.dtype('<i'+str(_bytes_per_sample))

    def __init__(self, config):
        Instrument.__init__(self, config)
        self._updates = None
        self._ip_address = None
        self._scope = None
        self._channels = None
        self._samples = None
        self._record_length = None
        self._x_zero = None
        self._x_increment = None

    def config(self, metadata, total_updates):
        """Configure the oscilloscope.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int

        :raises OSError: if unable to connect to oscilloscope
        """
        name = self.__class__.__name__
        self._updates = total_updates
        self._ip_address = PlaceConfig().get_config_value(name, "ip_address")
        self._scope = socket(AF_INET, SOCK_STREAM)
        self._scope.settimeout(5.0)
        try:
            self._scope.connect((self._ip_address, 4000))
        except OSError:
            self._scope.close()
            del self._scope
            raise
        self._channels = [self._is_active(
            x+1) for x in range(self._get_num_analog_channels())]
        self._record_length = self._get_record_length()
        metadata[name + '-record_length'] = self._record_length
        self._x_zero = [None for _ in self._channels]
        self._x_increment = [None for _ in self._channels]
        metadata[name + '-active_channels'] = self._channels
        self._samples = self._get_sample_rate()
        metadata[name + '-sample_rate'] = self._samples
        for channel, active in enumerate(self._channels):
            if not active:
                continue
            self._send_config_msg(channel+1)
            self._x_zero[channel] = self._get_x_zero(channel+1)
            self._x_increment[channel] = self._get_x_increment(channel+1)
            metadata[name +
                     '-ch{:d}_x_zero'.format(channel+1)] = self._x_zero[channel]
            metadata[name + '-ch{:d}_x_increment'.format(
                channel+1)] = self._x_increment[channel]
            metadata[name +
                     '-ch{:d}_y_zero'.format(channel+1)] = self._get_y_zero(channel+1)
            metadata[name +
                     '-ch{:d}_y_offset'.format(channel+1)] = self._get_y_offset(channel+1)
            metadata[name + '-ch{:d}_y_multiplier'.format(
                channel+1)] = self._get_y_multiplier(channel+1)
        self._scope.close()
        if self._config['plot']:
            for channel, active in enumerate(self._channels):
                if not active:
                    continue
                width, height = DEFAULT_FIGSIZE
                plt.figure(
                    name + '-ch{:d}'.format(channel+1),
                    figsize=(width, height*2),  # two subplots
                    dpi=DEFAULT_DPI
                )
                plt.clf()

    def update(self, update_number, progress):
        """Get data from the oscilloscope.

        :param update_number: the current update count
        :type update_number: int

        :param progress: data to send back to the web app
        :type progress: dict

        :returns: the trace data
        :rtype: numpy.array dtype='(*number_channels*,*number_samples*)int16'
        """
        self._scope = socket(AF_INET, SOCK_STREAM)
        self._scope.settimeout(5.0)
        self._scope.connect((self._ip_address, 4000))
        self._activate_acquisition()
        field = '{}-trace'.format(self.__class__.__name__)
        type_ = '({:d},{:d})int16'.format(
            len(self._channels), self._record_length)
        data = np.zeros((1,), dtype=[(field, type_)])
        for channel, active in enumerate(self._channels):
            if not active:
                continue
            self._request_curve(channel+1)
            trace = self._receive_curve()
            if self._config['plot']:
                self._plot(channel+1, trace, update_number, progress)
            data[field][0][channel] = trace
        self._scope.close()
        return data.copy()

    def cleanup(self, abort=False):
        """Nothing to cleanup"""
        pass

    def _clear_errors(self):
        self._scope.sendall(bytes(':*ESR?;:ALLEv?\n', encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')

    def _is_active(self, channel):
        self._scope.settimeout(5.0)
        self._clear_errors()
        self._scope.sendall(bytes(':DATA:SOURCE CH{:d};:WFMOUTPRE?\n'.format(channel),
                                  encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        self._scope.sendall(b'*ESR?\n')
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        self._clear_errors()
        return int(dat) == 0

    def _get_num_analog_channels(self):
        self._scope.settimeout(5.0)
        self._scope.sendall(b':CONFIGURATION:ANALOG:NUMCHANNELS?\n')
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return int(dat)

    def _get_x_zero(self, channel):
        self._scope.settimeout(5.0)
        self._scope.sendall(bytes(
            ':HEADER OFF;:DATA:SOURCE CH{:d};:WFMOUTPRE:XZERO?\n'.format(
                channel),
            encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_y_zero(self, channel):
        self._scope.settimeout(5.0)
        self._scope.sendall(bytes(
            ':HEADER OFF;:DATA:SOURCE CH{:d};:WFMOUTPRE:YZERO?\n'.format(
                channel),
            encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_x_increment(self, channel):
        self._scope.settimeout(5.0)
        self._scope.sendall(bytes(
            ':HEADER OFF;:DATA:SOURCE CH{:d};:WFMOUTPRE:XINCR?\n'.format(
                channel),
            encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_y_offset(self, channel):
        self._scope.settimeout(5.0)
        self._scope.sendall(bytes(
            ':HEADER OFF;:DATA:SOURCE CH{:d};:WFMOUTPRE:YOFF?\n'.format(
                channel),
            encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_y_multiplier(self, channel):
        self._scope.settimeout(5.0)
        self._scope.sendall(bytes(
            ':HEADER OFF;:DATA:SOURCE CH{:d};:WFMOUTPRE:YMULT?\n'.format(
                channel),
            encoding='ascii'))
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_sample_rate(self):
        self._scope.settimeout(5.0)
        self._scope.sendall(b':HEADER OFF;:HORIZONTAL:SAMPLERATE?\n')
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_record_length(self):
        self._scope.settimeout(5.0)
        self._scope.sendall(b':HEADER OFF;:HORIZONTAL:RECORDLENGTH?\n')
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return int(dat)

    def _send_config_msg(self, channel):
        config_msg = bytes(
            ':DATA:' + (
                'SOURCE CH{:d};'.format(channel) +
                'START 1;' +
                'STOP {};'.format(self._record_length)
            ) +
            ':WFMOUTPRE:' + (
                'BYT_NR 2;' +
                'BIT_NR 16;' +
                'ENCDG BINARY;' +
                'BN_FMT RI;' +
                'BYT_OR LSB;'
            ) +
            ':HEADER 0\n',
            encoding='ascii'
        )
        self._scope.sendall(config_msg)

    def _activate_acquisition(self):
        self._scope.sendall(b':ACQUIRE:STATE ON\n')
        sleep(0.1)
        if self._config['force_trigger']:
            self._force_trigger()
        else:
            self._wait_for_trigger()

    def _force_trigger(self):
        for _ in range(120):
            self._scope.settimeout(60)
            self._scope.sendall(b':TRIGGER FORCE\n')
            sleep(0.1)
            self._scope.settimeout(0.25)
            try:
                self._scope.recv(4096)
            except OSError:
                pass
            self._scope.settimeout(60)
            self._scope.sendall(b':ACQUIRE:STATE?\n')
            sleep(0.1)
            byte = b''
            for _ in range(600):
                byte = self._scope.recv(1)
                if byte == b'0' or byte == b'1':
                    self._scope.settimeout(0.25)
                    try:
                        self._scope.recv(4096)
                    except OSError:
                        pass
                    break
            if byte == b'0':
                break

    def _wait_for_trigger(self):
        self._scope.setblocking(False)
        for _ in range(120):
            self._scope.sendall(b':ACQUIRE:STATE?\n')
            byte = b''
            for _ in range(600):
                try:
                    byte = self._scope.recv(1)
                except BlockingIOError:
                    sleep(0.1)
                    continue
                if byte == b'0' or byte == b'1':
                    break

            if byte == b'0':
                break
            sleep(0.5)

    def _request_curve(self, channel):
        self._scope.settimeout(60.0)
        self._scope.sendall(
            bytes(':DATA:SOURCE CH{:d};:CURVE?\n'.format(channel), encoding='ascii'))

    def _receive_curve(self):
        hash_message = b''
        while hash_message != b'#':
            hash_message = self._scope.recv(1)

        length_length = int(self._scope.recv(1).decode(), base=16)
        length = int(self._scope.recv(length_length).decode(), base=10)
        data = b''
        while len(data) < length:
            data += self._scope.recv(4096)
        data = data[:length]
        return np.frombuffer(data, dtype='int16')

    def _plot(self, channel, trace, update_number, progress):
        times = np.arange(len(trace)) * \
            self._x_increment[channel-1] + self._x_zero[channel-1]
        name = self.__class__.__name__
        plt.figure(name + '-ch{:d}'.format(channel))
        # trace plot
        plt.subplot(211)
        plt.cla()
        plt.plot(times, trace)
        plt.xlabel('seconds')
        plt.ylim((-(2**15), 2**15))
        plt.title('Update {:03}'.format(update_number))
        plt.tight_layout()
        # wiggle plot
        plt.subplot(212)
        axes = plt.gca()
        data = trace / 2**15 + update_number
        axes.plot(data, times, color='black', linewidth=0.5)
        axes.fill_betweenx(
            times,
            data,
            update_number,
            where=data > update_number,
            color='black')
        plt.xlim((-1, self._updates))
        plt.xlabel('Update Number')
        plt.ylabel('seconds')
        plt.tight_layout()
        # save plot to progress
        self.plotter.png(
            name + '-ch{: d}'.format(channel),
            plt.gcf()
        )


class MSO3000andDPO3000Series(TektronixCommon):
    """PLACE device class for the MSO3000 and DPO3000 series oscilloscopes.

    This class is based on the programmers manual and should apply to the
    following devices: DPO3012, DPO3014, DPO3032, DPO3034, DPO3052, DPO3054,
    MSO3012, MSO3014, MSO3032, MSO3034, MSO3054.
    """
    pass


class MDO4000BCMSODPO4000BandMDO3000(TektronixCommon):
    """PLACE device class for the MDO4000-B-C-MSO-DPO4000B-and-MDO3000 series
    oscilloscopes."""
    pass


class DPO3014(MSO3000andDPO3000Series):
    """Subclass for the DPO3014"""
    pass


class MDO3014(MDO4000BCMSODPO4000BandMDO3000):
    """Subclass for the MDO3014"""
    pass
