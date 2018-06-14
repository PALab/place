"""Run an experiment"""
import os
import datetime
import json
from operator import attrgetter
from importlib import import_module
import pkg_resources
from numpy import datetime64 as npdatetime64  # pylint: disable=no-name-in-module
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
        total_steps = self.config['updates'] * len(self.plugins)
        self.progress.updating(total_steps)
        for update_number in range(self.config['updates']):
            self._run_update(update_number)

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

    def _run_update(self, update_number):
        """Run one update phase"""
        num_plugins = len(self.plugins)
        data = np.array([(npdatetime64(datetime.datetime.now()),)],
                        dtype=[('PLACE-time', 'datetime64[us]')])
        for plugin_number, plugin in enumerate(self.plugins):
            current_step = update_number * num_plugins + plugin_number
            current_plugin = plugin.__class__.__name__
            self.progress.set_progress(current_step, current_plugin)
            data = self._run_plugin_update(plugin, update_number, data)
            self.progress.set_progress(current_step + 1, current_plugin)

        # save data for this update
        filename = '{}/data_{:03d}.npy'.format(
            self.config['directory'], update_number)
        with open(filename, 'xb') as data_file:
            np.save(data_file, data.copy(), allow_pickle=False)

        # plotting phase loop
        for plugin in self.plugins:
            plot_data = plugin.plot(update_number, data.copy())
            if plot_data is not None:
                self.progress.set_plot_data(
                    plugin.__class__.__name__, plot_data)

    def _run_plugin_update(self, plugin, update_number, data):
        """Run the update phase on one PLACE plugin"""
        class_ = plugin.__class__
        try:
            if issubclass(class_, Instrument):
                new_data = plugin.update(update_number)
                if new_data is not None:
                    data = rfn.merge_arrays([data, new_data], flatten=True)
            elif issubclass(class_, PostProcessing):
                data = plugin.update(update_number, data.copy())
        except RuntimeError:
            self.cleanup_phase(abort=True)
            raise
        return data

    def get_progress(self):
        """Return a progress as a value from 0.0 to 1.0"""
        return self.progress.get_progress()

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
