"""Module for handling PLACE experiment progress"""
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
        self.directory = config['directory']
        self.current_phase = 'config'
        self.current_update = 0
        self.total_updates = config['updates']
        self.update_time = 0.0
        self.current_plugin = "none"
        self.plugin = {}
        # each plugin can manage its own progress in its own way
        # and it will be sent back to the Elm web application
        for plugin in config["plugins"]:
            try:
                self.plugin[plugin['elm_module_name']] = {}
            except KeyError:
                print('JSON sent to PLACE:\n{}'.format(plugin))
                print('The key "elm_module_name" is missing.')
                print('Please add it to the Elm module.')
                raise
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

    def to_dict(self):
        """Put all data into dictionary"""
        return {
            'directory': self.directory,
            'current_phase': self.current_phase,
            'current_update': self.current_update,
            'total_updates': self.total_updates,
            'update_time': self.update_time,
            'current_plugin': self.current_plugin,
            'plugin': self.plugin,
            'message': self.message
        }
