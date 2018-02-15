"""Module for exporting data to HDF5 format."""
import json
import numpy as np
try:
    from obspy.core import Stream, Trace
    from obspy.core.trace import Stats
except ImportError:
    raise ImportError("Use of the PAL H5 plugin for PLACE requires installing ObsPy")
from place.plugins.export import Export

class H5Output(Export):
    """Export class for exporting NumPy data into an H5 format.

    This module requires the following values to be specified in the JSON
    configuration:

    ============================== ========= ================================================
    Key                            Type      Meaning
    ============================== ========= ================================================
    trace_field                    str       the name of the PLACE field containing the trace
    x_position_field               str       the name of the PLACE field continaing the
                                             x-position data for linear movement (or empty if
                                             not being used).
    y_position_field               str       the name of the PLACE field continaing the
                                             y-position data for linear movement (or empty if
                                             not being used).
    theta_position_field           str       the name of the PLACE field continaing the
                                             theta-position data for rotational movement (or
                                             empty if not being used).
    header_sampling_rate_key       str       the name of metadata key containing the sampling
                                             rate to be used for the ObsPy traces
    header_samples_per_record_key  str       the name of metadata key containing the samples
                                             per record to be used for the ObsPy traces
    header_extra1_name             str       allows addition of arbitray data to the ObsPy
                                             header with this name
    header_extra1_val              str       value of the data
    header_extra2_name             str       allows addition of arbitray data to the ObsPy
                                             header with this name
    header_extra2_val              str       value of the data
    reprocess_path                 str       reprocess data in the given path instead of
                                             processing any new data
    ============================== ========= ================================================
    """

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
        data = _load_scandata(path)
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
        config_key = self._config['header_sampling_rate_key']
        try:
            header.sampling_rate = float(metadata[config_key])
        except KeyError:
            raise KeyError("The following key was not found in the metadata: " +
                           "{}. Did you set the correct ".format(config_key) +
                           "'sample rate metadata key' in PAL H5 Output module?")
        header.npts = int(metadata[self._config['header_samples_per_record_key']]) - 1
        try:
            if self._config['dd_300']:
                header.calib = metadata['dd_300_calibration']
            elif self._config['dd_900']:
                header.calib = metadata['dd_900_calibration']
            elif self._config['vd_08']:
                header.calib = metadata['vd_08_calibration']
            elif self._config['vd_09']:
                header.calib = metadata['vd_09_calibration']
        except KeyError:
            pass
        header.comments = str(config['comments'])
        header.place = metadata

        if self._config['header_extra1_name'] != '' and self._config['header_extra1_val'] != '':
            header[self._config['header_extra1_name']] = self._config['header_extra1_val']
        if self._config['header_extra2_name'] != '' and self._config['header_extra2_val'] != '':
            header[self._config['header_extra2_name']] = self._config['header_extra2_val']
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
            raise ValueError('Too many dimensions in trace data. Cannot make sense of it!')

def _load_config(path):
    with open(path + '/config.json', 'r') as file_p:
        return json.load(file_p)

def _load_scandata(path):
    with open(path + '/scan_data.npy', 'rb') as file_p:
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
