"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE.
"""
from time import sleep
from threading import Thread
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

    def config(self, metadata, total_updates):
        """Configure the counter

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        self._count = 0
        self._samples = 2**7
        self._data = np.recarray(
            (total_updates,),
            dtype=[('update', int), ('count', int), ('trace', object)])
        metadata['counter_samples'] = self._samples
        metadata['counter_sleep_time'] = self._config['sleep_time']

    def update(self, update_number, socket=None):
        """Update the counter

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param socket: connection to the webapp plot frame
        :type socket: websocket
        """
        self._count += 1
        trace = (np.random.rand(self._samples) - 0.5) * 2
        self._data[update_number] = (update_number, self._count, trace)
        if self._config['plot']:
            if update_number == 0:
                plt.clf()
            self._wiggle_plot(trace, socket=socket)
        sleep(self._config['sleep_time'])

    def cleanup(self, abort=False):
        """Stop the counter and return data.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool

        :returns: the data records for this instrument
        :rtype: numpy.recarray
        """
        if self._config['plot'] == 'yes':
            plt.close('all')
        return self._data

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
