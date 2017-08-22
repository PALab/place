"""Module for exporting data to HDF5 format."""
import json
import numpy as np
try:
    from obspy.core import Stream, Trace
    from obspy.core.trace import Stats
except ImportError:
    pass
from place.plugins.export import Export

class H5Output(Export):
    """Export class for exporting NumPy data into an H5 format.

    This module requires the following values to be specified in the JSON
    configuration:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    trace_field               str            the name of the PLACE field containing the trace
    x_position_field          str            the name of the PLACE field continaing the
                                             x-position data for linear movement (or empty if
                                             not being used).
    y_position_field          str            the name of the PLACE field continaing the
                                             y-position data for linear movement (or empty if
                                             not being used).
    theta_position_field      str            the name of the PLACE field continaing the
                                             theta-position data for rotational movement (or
                                             empty if not being used).
    header_extra1_name        str            allows addition of arbitray data to the H5
                                             header with this name
    header_extra1_val         str            value of the data
    header_extra2_name        str            allows addition of arbitray data to the H5
                                             header with this name
    header_extra2_val         str            value of the data
    ========================= ============== ================================================
    """

    def export(self, path):
        """Export the data to an H5 file.

        :param path: the path with the experimental data, config data, etc.
        :type path: str
        """
        header = self._init_header(path)
        data = _load_scandata(path)
        streams = [Stream() for _ in data[0][self._config['trace_field']]]
        for update in data:
            header.starttime = str(update['time'])
            self._add_position_data(update, header)
            trace = update[self._config['trace_field']]
            for channel_num, channel in enumerate(trace):
                if len(channel) > 1:
                    for record_num, record in enumerate(channel):
                        header.record = record_num
                        trace = Trace(data=record, header=header)
                        streams[channel_num].append(trace)
                else:
                    for record in channel:
                        trace = Trace(data=record, header=header)
                        streams[channel_num].append(trace)
        _write_streams(path, streams)

    def _init_header(self, path):
        metadata = _load_metadata(path)
        header = Stats()
        header.sampling_rate = float(metadata['sampling_rate'])
        header.npts = int(metadata['samples_per_record']) - 1
        header.comments = str(metadata['comments'])
        if self._config['header_extra1_name'] != '' and self._config['header_extra1_val'] != '':
            header[self._config['header_extra1_name']] = self._config['header_extra1_val']
        if self._config['header_extra2_name'] != '' and self._config['header_extra2_val'] != '':
            header[self._config['header_extra2_name']] = self._config['header_extra2_val']
        return header

    def _add_position_data(self, update, header):
        if self._config['x_position_field'] != '':
            header.x_position = update[self._config['x_position_field']]
        if self._config['y_position_field'] != '':
            header.y_position = update[self._config['y_position_field']]
        if self._config['theta_position_field'] != '':
            header.theta_position = update[self._config['theta_position_field']]

def _load_metadata(path):
    with open(path + '/meta.json', 'r') as file_p:
        return json.load(file_p)

def _load_scandata(path):
    with open(path + '/scan_data.npy', 'rb') as file_p:
        return np.load(file_p)

def _write_streams(path, streams):
    for stream_num, stream in enumerate(streams):
        stream.write(path + '/channel_{}.h5'.format(stream_num), format='H5')
