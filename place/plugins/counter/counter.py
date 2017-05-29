"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE.
Read about this plugin at:
    https://github.com/PALab/place/blob/master/WRITING_PLUGINS.md#example-software-counter
"""
from time import sleep
from threading import Thread
import json
import mpld3
import matplotlib.pyplot as plt
import numpy as np
from place.plugins.instrument import Instrument, send_data_thread

class Counter(Instrument):
    """A unit counter"""
    def __init__(self, config):
        """Initialize the counter, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self._count = None
        self._samples = None
        self._data = None
        self._directory = None

    def config(self, metadata, updates, directory):
        """Configure the counter

        :param metadata: metadata for the scan
        :type metadata: dict

        :param updates: number of update that will be performed
        :type updates: int

        :param directory: a directory in which this instrument should write data
        :type directory: str
        """
        self._count = 0
        self._samples = 2**7
        self._data = np.zeros((updates, self._samples))
        self._directory = directory
        metadata['counter_samples'] = self._samples
        metadata['counter_sleep_time'] = self._config['sleep_time']
        with open(self._directory + '/counter_meta.json', 'x') as meta_file:
            json.dump(metadata, meta_file, indent=2)

    def update(self, metadata, update_number, socket=None):
        """Update the counter

        :param metadata: metadata for the scan
        :type metadata: dict

        :param update_number: the number of the current update (1-indexed)
        :type update_number: int

        :param socket: connection to the webapp plot frame
        :type socket: websocket
        """
        self._count += 1
        metadata['counter_current_count'] = self._count
        trace = (np.random.rand(2**7) - 0.5) * 2
        if self._config['plot']:
            if update_number == 1:
                plt.clf()
            self._wiggle_plot(trace, socket=socket)
        self._data[self._count-1] = trace
        sleep(self._config['sleep_time'])

    def cleanup(self, abort=False):
        """Stop the counter and return data.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool
        """
        with open(self._directory + '/counter_data.npy', 'xb') as data_file:
            np.save(data_file, self._data)
        if self._config['plot'] == 'yes':
            plt.close('all')

    def _wiggle_plot(self, trace, socket=None):
        """Plot the data as a wiggle plot.

        Plots to socket using mpld3, if available, otherwise uses standard
        matplotlib backend.
        """
        if socket is None:
            plt.ion()
        self._make_plot(trace)
        if socket is None:
            plt.pause(0.05)
        else:
            out = mpld3.fig_to_html(plt.gcf())
            thread = Thread(target=send_data_thread, args=(socket, out))
            thread.start()
            thread.join()

    def _make_plot(self, trace):
        """Generate the plot for either sending or painting."""
        axes = plt.gca()
        times = np.arange(0, self._samples)
        trace += self._count
        axes.fill_betweenx(
            times,
            trace,
            self._count,
            where=trace > self._count,
            color='black')
        plt.xlim((1, len(self._data) + 1))
        plt.xlabel('Update Number')
        plt.ylim((self._samples, 0))
        plt.ylabel('Dummy Data')
