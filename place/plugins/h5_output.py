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
    """Export class for exporting NumPy data into an H5 format."""
    def export(self, path):
        """Export the data to an H5 file.

        :param path: the path with the experimental data, config data, etc.
        :type path: str
        """
        with open(path + '/meta.json', 'r') as file_p:
            metadata = json.load(file_p)
        with open(path + '/scan_data.npy', 'rb') as file_p:
            data = np.load(file_p)

        header = Stats()
        header.sampling_rate = float(metadata['sampling_rate'])
        header.npts = int(metadata['samples_per_record']) - 1
        header.comments = str(metadata['comments'])

        trace_field = self._config['field']
        streams = [Stream() for _ in data[0][trace_field]]

        for update in data:
            header.starttime = str(update['time'])
            if self._config['x_position_field'] != '':
                header.x_position = update[self._config['x_position_field']]
            if self._config['y_position_field'] != '':
                header.y_position = update[self._config['y_position_field']]
            if self._config['theta_position_field'] != '':
                header.theta_position = update[self._config['theta_position_field']]
            trace = update[trace_field]
            for num, channel in enumerate(trace):
                for record in channel:
                    trace = Trace(data=record, header=header)
                    streams[num].append(trace)

        for num, stream in enumerate(streams):
            stream.write(path + '/channel_{}.h5'.format(num), format='H5')
