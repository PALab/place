"""Run an experiment"""
import os
import datetime
import json
from operator import attrgetter
from importlib import import_module
import pkg_resources
import numpy as np
from numpy.lib import recfunctions as rfn
from .plugins.instrument import Instrument
from .plugins.postprocessing import PostProcessing
from .plugins.export import Export
from .utilities import build_single_file
from .place_progress import PlaceProgress


class BasicExperiment:
    """Basic experiment class

    This is the first (and so far, only) experiment class in PLACE. It takes
    in configuration data for a variety of instruments. Each instrument must
    have a priority value. This experiment uses the priority order to execute
    a specified number of updates on each instrument. Data is collected from
    the instruments and saved as a NumPy record array.

    Even if the instruments used do not produce their own data, PLACE will
    still output a timestamp (with microsecond precision) into the
    experimental data:

    +---------------+-------------------------+-------------------------+
    | Heading       | Type                    | Meaning                 |
    +===============+=========================+=========================+
    | PLACE-time    | numpy.datetime64[us]    | timestamp from the      |
    |               |                         | system clock, taken at  |
    |               |                         | the beginning of each   |
    |               |                         | update                  |
    +---------------+-------------------------+-------------------------+
    """

    def __init__(self, config):
        """Experiment constructor

        :param config: a decoded JSON dictionary
        :type config: dict
        """
        version = pkg_resources.require("place")[0].version
        self.config = config
        self.plugins = []
        self.metadata = {'PLACE_version': version}
        self.progress = PlaceProgress()
        self._create_experiment_directory()
        self.init_phase()

    def run(self):
        """Run the experiment."""
        self.progress.started()
        self.config_phase()
        self.update_phase()
        self.cleanup_phase(abort=False)
        self.progress.finished()

    def init_phase(self):
        """Initialize the plugins.

        During this phase, all plugins receive their configuration data and
        should store it. The list of plugins being used by the experiment is
        created and sorted by their priority level. No physical configuration
        should occur during this phase.
        """
        self.progress.initializing(len(self.config['plugins']))
        for module_number, module in enumerate(self.config['plugins']):
            self.progress.set_progress(module_number, module['class_name'])
            module_name = module['module_name']
            class_string = module['class_name']
            priority = module['priority']
            config = module['config']

            plugin = _programmatic_import(module_name, class_string, config)
            plugin.priority = priority
            self.plugins.append(plugin)
            self.progress.set_progress(module_number + 1)

        # sort plugins based on priority
        self.plugins.sort(key=attrgetter('priority'))

    def config_phase(self):
        """Configure the instruments and post-processing plugins.

        During the configuration phase, instruments and post-processing plugins
        are provided with their configuration data. Metadata is collected from
        all plugins and written to disk.
        """
        self.progress.configuring(len(self.plugins))
        for module_number, module in enumerate(self.plugins):
            self.progress.set_progress(
                module_number, module.__class__.__name__)
            try:
                config_func = module.config
            except AttributeError:
                continue
            config_func(self.metadata, self.config['updates'])
            self.progress.set_progress(module_number + 1)

        self.config['metadata'] = self.metadata
        with open(self.config['directory'] + '/config.json', 'x') as config_file:
            json.dump(self.config, config_file, indent=2, sort_keys=True)

    def update_phase(self):
        """Perform all the updates on the plugins.

        The update phase occurs *N* times, based on the user configuration for
        the experiment. This function loops over the instruments and
        post-processing plugins (based on their priority) and calls their
        update method.

        One NumPy file will be written for each update. If the experiement
        completes normally, these files will be merged into a single NumPy
        file.
        """
        num_plugins = len(self.plugins)
        self.progress.updating(self.config['updates'] * num_plugins)
        for update_number in range(self.config['updates']):
            current_data = np.array([(np.datetime64(datetime.datetime.now()),)],  # pylint: disable=no-member
                                    dtype=[('PLACE-time', 'datetime64[us]')])

            for module_number, module in enumerate(self.plugins):
                self.progress.set_progress(update_number * num_plugins + module_number,
                                           module.__class__.__name__)
                class_ = module.__class__
                if issubclass(class_, Instrument):
                    try:
                        module_data, plot_data = module.update(update_number)
                    except RuntimeError:
                        self.cleanup_phase(abort=True)
                        raise
                    if module_data is not None:
                        current_data = rfn.merge_arrays([current_data, module_data],
                                                        flatten=True)
                    if plot_data is not None:
                        self.progress.set_plot_data(
                            module.__class__.__name__, plot_data)
                elif issubclass(class_, PostProcessing):
                    current_data = module.update(
                        update_number, current_data.copy())
                self.progress.set_progress(update_number * num_plugins + module_number + 1,
                                           module.__class__.__name__)
            filename = '{}/data_{:03d}.npy'.format(
                self.config['directory'], update_number)
            with open(filename, 'xb') as data_file:
                np.save(data_file, current_data.copy(), allow_pickle=False)

    def cleanup_phase(self, abort=False):
        """Cleanup the plugins.

        During this phase, each module has its cleanup method called. If the
        abort flag has not been set in the cleanup call, this will be passed to
        the module.

        :param abort: signals that the experiment is being aborted
        :type abort: bool
        """
        if abort:
            for plugin in self.plugins:
                plugin.cleanup(abort=True)
        else:
            self.progress.cleaning(len(self.plugins))
            build_single_file(self.config['directory'])
            for plugin_number, plugin in enumerate(self.plugins):
                self.progress.set_progress(
                    plugin_number, plugin.__class__.__name__)
                class_ = plugin.__class__
                if issubclass(class_, Export):
                    plugin.export(self.config['directory'])
                else:
                    plugin.cleanup(abort=False)
                self.progress.set_progress(
                    plugin_number + 1, plugin.__class__.__name__)

    def _create_experiment_directory(self):
        self.config['directory'] = os.path.abspath(
            os.path.expanduser(self.config['directory']))
        if not os.path.exists(self.config['directory']):
            os.makedirs(self.config['directory'])
        else:
            for i in range(1, 1000):
                if not os.path.exists(self.config['directory'] + '-' + str(i)):
                    self.config['directory'] += '-' + str(i)
                    break
            print('Experiment path exists - saving to ' +
                  self.config['directory'])
            os.makedirs(self.config['directory'])

    def get_progress_string(self):
        """Return a progress string"""
        return str(self.progress)

    def get_liveplot_bytes(self, class_name):
        """Return the bytes for the liveplot"""
        return self.progress.liveplots[class_name]

    def is_finished(self):
        """Is the experiment finished"""
        return self.progress.is_finished()


def _programmatic_import(module_name, class_name, config):
    """Import a module based on string input.

    This function takes a string for a module and a string for a class and
    imports that class from the given module programmatically.

    :param module_name: the name of the module to import from
    :type module_name: str

    :param class_name: the string of the class to import
    :type class_name: str

    :param config: the JSON configuration data for the module
    :type config: dict

    :returns: an instance of the module matching the class and module name
    :rtype: Instrument, PostProcessing, or Export object

    :raises TypeError: if requested module has not been subclassed correctly
    """
    module = import_module('place.plugins.' + module_name)
    class_ = getattr(module, class_name)
    if (not issubclass(class_, Instrument) and
            not issubclass(class_, PostProcessing) and
            not issubclass(class_, Export)):
        raise TypeError(class_name + " is not a PLACE subclass")
    return class_(config)
