"""Tektronix oscilloscope."""

from time import sleep
from socket import socket, AF_INET, SOCK_STREAM
import numpy as np
import matplotlib.pyplot as plt
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

class MSO3000andDPO3000Series(Instrument):
    """PLACE device class for the MSO3000 and DPO3000 series oscilloscopes.

    This class is based on the programmers manual and should apply to the
    following devices: DPO3012, DPO3014, DPO3032, DPO3034, DPO3052, DPO3054,
    MSO3012, MSO3014, MSO3032, MSO3034, MSO3054.
    """
    _bytes_per_sample = 2
    _data_type = np.dtype('<i'+str(_bytes_per_sample)) # (<)little-endian, (i)signed integer

    def __init__(self, config):
        Instrument.__init__(self, config)
        self._updates = None
        self._ip_address = None
        self._scope = None
        self._x_zero = None
        self._x_increment = None

    def config(self, metadata, total_updates):
        """Configure the oscilloscope.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int
        """
        name = self.__class__.__name__
        self._updates = total_updates
        self._ip_address = PlaceConfig().get_config_value(name, "ip_address")
        self._scope = socket(AF_INET, SOCK_STREAM)
        self._scope.settimeout(5.0)
        self._scope.connect((self._ip_address, 4000))
        self._send_config_msg()
        metadata[name + '_sample_rate'] = self._get_sample_rate()
        self._x_zero = self._get_x_zero()
        metadata[name + '_x_zero'] = self._x_zero
        self._x_increment = self._get_x_increment()
        metadata[name + '_x_increment'] = self._x_increment
        self._scope.close()
        if self._config['plot']:
            plt.figure(name)
            plt.clf()
            plt.ion()

    def update(self, update_number):
        """Get data from the oscilloscope.

        :param update_number: the current update count
        :type update_number: int

        :returns: the trace data
        :rtype: numpy.array dtype='(*number_samples*,)int16'
        """
        self._scope = socket(AF_INET, SOCK_STREAM)
        self._scope.settimeout(5.0)
        self._scope.connect((self._ip_address, 4000))
        self._activate_acquisition()
        self._request_curve()
        trace = self._receive_curve()
        if self._config['plot']:
            self._plot(trace, update_number)
        data = np.zeros((1,), dtype=[('trace', '({},)int16'.format(len(trace)))])
        data['trace'][0] = trace
        return data.copy()

    def cleanup(self, abort=False):
        """Stop picomotor and end scan.

        :param abort: indicates the scan is being aborted rather than having
                      finished normally
        :type abort: bool
        """
        if abort is False and self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

    def _get_x_zero(self):
        self._scope.settimeout(5.0)
        self._scope.sendall(b':HEADER OFF;:WFMOUTPRE:XZERO?\n')
        dat = ''
        while '\n' not in dat:
            dat += self._scope.recv(4096).decode('ascii')
        return float(dat)

    def _get_x_increment(self):
        self._scope.settimeout(5.0)
        self._scope.sendall(b':HEADER OFF;:WFMOUTPRE:XINCR?\n')
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

    def _send_config_msg(self):
        config_msg = bytes(
            ':DATA:' + (
                'SOURCE CH1;' +
                'START 1;' +
                'STOP {};'.format(self._config['record_length'])
            ) +
            ':HORIZONTAL:' + (
                'RECORDLENGTH {};'.format(self._config['record_length']) +
                'DELAY:' + (
                    'MODE ON;' +
                    'TIME 0.0E+0'
                )
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
        activate_msg = b':ACQUIRE:STATE ON\n'
        self._scope.sendall(activate_msg)
        if self._config['force_trigger']:
            self._force_trigger()
        else:
            self._wait_for_trigger()

    def _force_trigger(self):
        self._scope.sendall(b':TRIGGER\n')

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

    def _request_curve(self):
        self._scope.settimeout(60.0)
        self._scope.sendall(b':CURVE?\n')

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
        self._scope.close()
        return np.frombuffer(data, dtype='int16')

    def _plot(self, trace, update_number):
        times = np.arange(len(trace)) * self._x_increment + self._x_zero

        plt.subplot(211)
        plt.cla()
        plt.plot(times, trace)
        plt.xlabel('seconds')
        plt.ylim((-(2**15), 2**15))
        plt.title('Update {:03}'.format(update_number))
        plt.tight_layout()
        plt.pause(0.05)

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
        plt.pause(0.05)

class DPO3014(MSO3000andDPO3000Series):
    """Subclass for the DPO3014"""
    pass
