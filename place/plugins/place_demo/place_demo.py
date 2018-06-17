"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE. It can generate
plots of "dummy data", similar to the data produced by the AlazarTech module.
It is great for showing how PLACE operates without setting up any hardware.
"""
from time import sleep
import numpy as np
from place.plugins.instrument import Instrument


class PlaceDemo(Instrument):
    """Demo instrument.

    The original idea for this device was to be a programming demo for the most
    basic device conceivable -- a unit counter. However, it soon became
    apparent that this class was useful as a software test of the PLACE system
    and it is now used to test: configuration importing, data collection,
    plotting, and other subsystems in PLACE. It can also be used as a quick way
    to verify that a PLACE installation has been successful.

    ``PlaceDemo`` requires only ``sleep_time``, ``number_of_points``, and
    ``plot`` values. Simple metadata is recorded to verify the metadata code.
    """

    def __init__(self, config):
        """Initialize the counter, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self._count = None
        self._number = None
        self._samples = None
        self._updates = None

    def config(self, metadata, total_updates):
        """Calculate basic values and record basic metadata.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        self._count = 0
        self._samples = self._config['number_of_points']
        self._updates = total_updates
        metadata['{}_samples'.format(self.__class__.__name__)] = self._samples

    def update(self, update_number):
        """Increment the counter.

        Additionally, this will generate a random trace, plot the trace, and
        return the trace in standard PLACE format. A sleep is performed between
        updates based on the user-provided ``sleep_time`` configuration.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: the current count (1-indexed) and a dummy trace in a numpy
                  record array
        :rtype: numpy.recarray
        """
        self._count += 1
        self._number = update_number
        samples = np.array(
            [np.exp(-i) * np.sin(2*np.pi*i) for i in np.arange(self._samples) * 0.05])
        noise = np.random.normal(
            0, 0.15, self._samples)  # pylint: disable=no-member
        trace = (samples + noise + 1) * 2**13
        count_field = '{}-count'.format(self.__class__.__name__)
        trace_field = '{}-trace'.format(self.__class__.__name__)
        data = np.array(
            [(self._count, trace)],
            dtype=[(count_field, 'int16'), (trace_field, 'float64', self._samples)])
        sleep(self._config['sleep_time'])
        return data

    def plot(self, update_number, data):
        """Return plot data for plotting in the web app.

        :param update_number: The count of the current update. This will start at 0.
        :type update_number: int

        :param data: The data array for this update.
        :type data: numpy.recarray

        :returns: The plot data as a list of dictionaries
        :rtype: [dict]
        """
        if not self._config['plot']:
            return None
        ydata = data[0]['{}-trace'.format(self.__class__.__name__)]
        xdata = np.arange(len(ydata))
        return [{
            'title': 'PLACE generated signal + noise',
            'xaxis': 'sample count',
            'yaxis': 'signal level',
            'series': [
                {
                    'name': 'demo data',
                    'xdata': xdata,
                    'ydata': ydata
                },
            ],
        }]

    def cleanup(self, abort=False):
        """Stop the demo and cleanup.

        :param abort: ``True`` if the experiement is being aborted, in which
                      case plotting should not occur
        :type abort: bool
        """
        pass
