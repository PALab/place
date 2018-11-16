"""Module for exporting data to HDF5 format."""
import json
import re
from warnings import warn
import numpy as np
try:
    from obspy.core import Stream, Trace
    from obspy.core.trace import Stats
except ImportError:
    warn("Use of the PAL H5 plugin for PLACE requires installing ObsPy")
from place.plugins.export import Export

_NUMBER = r'[-+]?\d*\.\d+|\d+'


class H5Output(Export):
    """Export class for exporting NumPy data into an H5 format."""

    def export(self, path):
        """Export the trace data to an H5 file.

        If the trace data contains two dimension, the first is assumed to be
        the channel, and the second is assumed to be the trace data.

        If the trace data contains three dimensions, the first is assumed to be
        the channel, the second is assumed to be the record number, with the
        third containing the trace data.

        If the trace data contains additional dimensions, this module will
        throw an error.

        When more than one channel is detected, each will be written to a
        different .h5 file.

        :param path: the path with the experimental data, config data, etc.
        :type path: str

        :raises ValueError: if trace data has more than three dimensions
        """
        if self._config['reprocess'] != '':
            path = self._config['reprocess']
        header = self._init_header(path)
        data = _load_data(path)
        streams = self._get_channel_streams(data)
        for update in data:
            header.starttime = str(update['time'])
            self._add_position_data(update, header)
            self._process_trace(update, streams, header)
        _write_streams(path, streams)

    def _init_header(self, path):
        config = _load_config(path)
        metadata = config['metadata']
        header = Stats()

        if 'ATS9440' in config['plugins'].keys():
            ats_config = config['plugins']['ATS9440']['config']
        elif 'ATS660' in config['plugins'].keys():
            ats_config = config['plugins']['ATS660']['config']
        else:
            raise KeyError('Cannot locate trace config data')

        if 'Polytec' in config['plugins'].keys():
            polytec_config = config['plugins']['Polytec']['config']
        else:
            raise KeyError('Cannot locate vibrometer config data')

        header.sampling_rate = _calc_sampling_rate(ats_config['sample_rate'])
        header.npts = int(ats_config['pre_trigger_samples'] +
                          ats_config['post_trigger_samples']) - 1

        if polytec_config['dd_300']:
            header.calib = float(re.findall(
                _NUMBER, polytec_config['dd_300_range'])[0])
        elif polytec_config['dd_900']:
            header.calib = float(re.findall(
                _NUMBER, polytec_config['dd_900_range'])[0])
        elif polytec_config['vd_08']:
            header.calib = float(re.findall(
                _NUMBER, polytec_config['vd_08_range'])[0])
        elif polytec_config['vd_09']:
            header.calib = float(re.findall(
                _NUMBER, polytec_config['vd_09_range'])[0])
        else:
            raise KeyError('Cannot locate vibrometer calibration data')

        header.comments = str(config['comments'])
        header.place = metadata

        if self._config['header_extra1_name'] != '' and self._config['header_extra1_val'] != '':
            header[self._config['header_extra1_name']
                   ] = self._config['header_extra1_val']
        if self._config['header_extra2_name'] != '' and self._config['header_extra2_val'] != '':
            header[self._config['header_extra2_name']
                   ] = self._config['header_extra2_val']
        return header

    def _get_channel_streams(self, data):
        """Returns a list of empty ObsPy streans.

        This method returns a single channel stream if the trace data is one
        dimensional. If the data is multidimensional, the first dimension is
        assumed to be the channel, and this method then returns an ObsPy stream
        for each channel.
        """
        first_trace = data[0][self._config['trace_field']]
        if len(first_trace.shape) == 1:
            return [Stream()]
        return [Stream() for _ in first_trace]

    def _add_position_data(self, update, header):
        if self._config['x_position_field'] != '':
            header.x_position = update[self._config['x_position_field']]
        if self._config['y_position_field'] != '':
            header.y_position = update[self._config['y_position_field']]
        if self._config['theta_position_field'] != '':
            header.theta_position = update[self._config['theta_position_field']]

    def _process_trace(self, update, streams, header):
        trace = update[self._config['trace_field']]
        dimensions = len(trace.shape)
        if dimensions == 1:
            _trace_1d(streams, trace, header)
        elif dimensions == 2:
            _trace_2d(streams, trace, header)
        elif dimensions == 3:
            _trace_3d(streams, trace, header)
        else:
            raise ValueError(
                'Too many dimensions in trace data. Cannot make sense of it!')


def _load_config(path):
    with open(path + '/config.json', 'r') as file_p:
        return json.load(file_p)


def _load_data(path):
    with open(path + '/data.npy', 'rb') as file_p:
        return np.load(file_p)


def _write_streams(path, streams):
    for stream_num, stream in enumerate(streams, start=1):
        stream.write(path + '/channel_{}.h5'.format(stream_num), format='H5')


def _trace_1d(streams, trace, header):
    obspy_trace = Trace(data=trace, header=header)
    streams[0].append(obspy_trace)


def _trace_2d(streams, trace, header):
    for channel_num, channel in enumerate(trace):
        obspy_trace = Trace(data=channel, header=header)
        streams[channel_num].append(obspy_trace)


def _trace_3d(streams, trace, header):
    for channel_num, channel in enumerate(trace):
        num_records = len(channel)
        for record_num, record in enumerate(channel):
            if num_records > 1:
                header.record = record_num
            obspy_trace = Trace(data=record, header=header)
            streams[channel_num].append(obspy_trace)


def _calc_sampling_rate(const_str):
    options = {
        'SAMPLE_RATE_1KSPS':         1000,
        'SAMPLE_RATE_2KSPS':         2000,
        'SAMPLE_RATE_5KSPS':         5000,
        'SAMPLE_RATE_10KSPS':       10000,
        'SAMPLE_RATE_20KSPS':       20000,
        'SAMPLE_RATE_50KSPS':       50000,
        'SAMPLE_RATE_100KSPS':     100000,
        'SAMPLE_RATE_200KSPS':     200000,
        'SAMPLE_RATE_500KSPS':     500000,
        'SAMPLE_RATE_1MSPS':      1000000,
        'SAMPLE_RATE_2MSPS':      2000000,
        'SAMPLE_RATE_5MSPS':      5000000,
        'SAMPLE_RATE_10MSPS':    10000000,
        'SAMPLE_RATE_20MSPS':    20000000,
        'SAMPLE_RATE_25MSPS':    25000000,
        'SAMPLE_RATE_50MSPS':    50000000,
        'SAMPLE_RATE_100MSPS':  100000000,
        'SAMPLE_RATE_125MSPS':  125000000,
        'SAMPLE_RATE_160MSPS':  160000000,
        'SAMPLE_RATE_180MSPS':  180000000,
        'SAMPLE_RATE_200MSPS':  200000000,
        'SAMPLE_RATE_250MSPS':  250000000,
        'SAMPLE_RATE_400MSPS':  400000000,
        'SAMPLE_RATE_500MSPS':  500000000,
        'SAMPLE_RATE_800MSPS':  800000000,
        'SAMPLE_RATE_1000MSPS': 1000000000,
        'SAMPLE_RATE_1200MSPS': 1200000000,
        'SAMPLE_RATE_1500MSPS': 1500000000,
        'SAMPLE_RATE_1600MSPS': 1600000000,
        'SAMPLE_RATE_1800MSPS': 1800000000,
        'SAMPLE_RATE_2000MSPS': 2000000000,
        'SAMPLE_RATE_2400MSPS': 2400000000,
        'SAMPLE_RATE_3000MSPS': 3000000000,
        'SAMPLE_RATE_3600MSPS': 3600000000,
        'SAMPLE_RATE_4000MSPS': 4000000000
    }
    return options[const_str]
