"""A PLACE time module for controlling the timing of updates

This module is not associated with any hardware, but is
simply a tool to control the timiing of updates within a
PLACE experiment.
"""
import time
import numpy as np
from place.plugins.instrument import Instrument


class PlaceTimer(Instrument):
    """Time instrument.
    """

    def __init__(self, config, plotter):
        """Initialize the timer, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self.constant_interval = True
        self.wait_on_last_update = False
        self.updates = 0
        self.constant_wait_time = 1
        self.last_update_end = None

    def config(self, metadata, total_updates):
        """Calculate basic values and record basic metadata.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        if self._config['interval_type'] == "constant":
            self.constant_interval = True
        else:
            self.constant_interval = False
        self.wait_on_last_update = self._config['wait_on_last_update']
        self.updates = total_updates
        self.constant_wait_time = self._config['constant_wait_time']
        if self.constant_interval:
            metadata['{}_seconds_between_updates'.format(self.__class__.__name__)] = self.constant_wait_time
        self.last_update_end = time.time()

    def update(self, update_number, progress):
        """Increment the counter.

        Additionally, this will generate a random trace, plot the trace, and
        return the trace in standard PLACE format. A sleep is performed between
        updates based on the user-provided ``sleep_time`` configuration.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: A blank dictionary for sending data back to the frontend
        :type progress: dict
        """

        if self.constant_interval:
            if self.wait_on_last_update or (self.updates - update_number) > 1:
                wait_time = max(0.0, self.constant_wait_time - (time.time() - self.last_update_end))
                time.sleep(wait_time)

        self.last_update_end = time.time()

    def cleanup(self, abort=False):
        """Stop the demo and cleanup.

        :param abort: ``True`` if the experiement is being aborted, in which
                      case plotting should not occur
        :type abort: bool
        """
        return
