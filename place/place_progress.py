"""Module for handling PLACE experiment progress"""
class PlaceProgress:
    """A class to handle the progress of PLACE experiment

    The lifecycle of an experiment goes through these stages:

    1. Created
    2. Started
    3. Initializing
    4. Configuring
    5. Updating
    6. Cleaning
    7. Finished

    """
    def __init__(self):
        self._stage = 'Created'
        self._progress = -1
        self._total = -1
        self._plugin = 'None'
        self.liveplots = {}

    def __str__(self):
        if self._total == -1:
            return 'Experiment created'
        if self._total == -2:
            return 'Experiment finished'
        return 'Experiment {}: {:.2f}%{}'.format(
            self._stage,
            100 * self._progress / self._total,
            ('' if self._plugin == 'None' else (' ({})'.format(self._plugin)))
            )

    def started(self):
        """Call this when the experiment starts"""
        self._stage = 'Started'
        self._plugin = 'None'

    def initializing(self, total):
        """Call this when the experiment starts initializing"""
        self._stage = 'Initializing'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def configuring(self, total):
        """Call this when the experiment starts configuring"""
        self._stage = 'Configuring'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def updating(self, total):
        """Call this when the experiment starts updating"""
        self._stage = 'Updating'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def cleaning(self, total):
        """Call this when the experiment starts cleaning up"""
        self._stage = 'Cleaning'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def finished(self):
        """Call this when the experiment is finished"""
        self._stage = 'Finished'
        self._progress = -2
        self._total = -2
        self._plugin = 'None'

    def set_progress(self, progress, plugin='None'):
        """Call this to update the plugin and progress"""
        self._progress = progress
        self._plugin = plugin

    def set_plot_data(self, class_name, data):
        """Set the internal plot data for a running experiment"""
        self.liveplots[class_name] = data

    def is_finished(self):
        """Is the experiment finished"""
        return self._stage == 'Finished'
