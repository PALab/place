"""Module for handling PLACE experiment progress"""
from time import time
import json


class PlaceProgress:
    """A class to handle the progress of a PLACE experiment

    This class is used to maintain the progress state of a PLACE experiment
    and make it available to the web interface upon request.

    Specifically, includes information about:

    - Approximate start time for the experiment
    - The current phase of the experiment
    - The current update number and the number of total updates in the update
      phase
    - The current plugin that is running and, optionally, the progress of
      that plugin
    """

    def __init__(self, config):
        self.start_time = time()
        self.directory = config['directory']
        self.current_phase = 'config'
        self.current_update = 0
        self.total_updates = config['updates']
        self.update_times = []
        self.current_plugin = "none"
        self.plugin = {}
        # each plugin can manage its own progress in its own way
        for plugin in config["plugins"]:
            self.plugin[plugin['class_name']] = {}
        self.message = ""  # text to display in webapp

    def log(self, phase, plugin):
        """Set the phase and plugin status"""
        if phase not in ["none", "config", "update", "cleanup", "error"]:
            raise ValueError('phase cannot be set to "{}"'.format(phase))
        if plugin not in self.plugin.keys() and plugin != "none":
            raise ValueError('plugin cannot be set to "{}"'.format(plugin))
        self.current_plugin = plugin
        self.current_phase = phase

    def start_update(self, num):
        """Record the current update and log the start time of an update"""
        self.current_update = num
        self.update_times.append(time())

    def to_json(self):
        """Convert progress to JSON string and return"""
        return json.dumps(
            {
                # TODO 'start_time':
                'directory': self.directory,
                'current_phase': self.current_phase,
                'current_update': self.current_update,
                'total_updates': self.total_updates,
                # TODO 'update_times':
                'current_plugin': self.current_plugin,
                'plugin': self.plugin,
                'message': self.message
            })
