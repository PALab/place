"""Run an experiment"""
import datetime
import json
import os
from importlib import import_module
from operator import attrgetter
from time import time
from threading import Event
import copy
import traceback

import pkg_resources
import numpy as np
from numpy import datetime64 as npdatetime64  # pylint: disable=no-name-in-module
from numpy.lib import recfunctions as rfn

from placeweb.settings import MEDIA_ROOT

from .place_progress import PlaceProgress
from .plots import PlacePlotter
from .plugins.export import Export
from .plugins.instrument import Instrument
from .plugins.postprocessing import PostProcessing
from .utilities import build_single_file


class AbortExperiment(Exception):
    """Custom exceptions for aborting an experiment"""
    pass


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
        self.abort_event = Event()
        self.config = config
        self.plugins = []
        
        self.metadata = {
            'PLACE_version': version,
            'timestamp': int(round(time() * 1000)),  # milliseconds since epoch
        }
        self.config['metadata'] = self.metadata
        self.progress = PlaceProgress(config)
        self.progress.update_time = 0.0
        self._create_experiment_directory()

        # save config data right away in case we need to reload the settings
        with open(self.config['directory'] + '/config.json', 'x') as config_file:
            json.dump(_remove_specific_items(self.config),
                      config_file, indent=2, sort_keys=True)

        self.init_phase()

    def run(self, error_queue):
        """Run the experiment"""
        try:
            self.config_phase()
            self.update_phase()
            self.cleanup_phase()
        except AbortExperiment:
            self.cleanup_phase(abort=True)
        except Exception as e:
            traceback_message = traceback.format_exc()
            error_queue.put((e, traceback_message))
            raise(e)

    def init_phase(self):
        """Initialize the plugins

        During this phase, all plugins receive their configuration data and
        should store it. The list of plugins being used by the experiment is
        created and sorted by their priority level. No physical configuration
        should occur during this phase.
        """
        for elm_name, plugin_data in self.config['plugins'].items():
            if self.abort_event.is_set():
                raise AbortExperiment

            # get import details for plugin's Python code
            try:
                python_module_name = plugin_data['metadata']['python_module_name']
                python_class_name = plugin_data['metadata']['python_class_name']
            except KeyError:
                raise KeyError(
                    'Could not find key in module: {}, {}'.format(elm_name, plugin_data))

            # get the progress dictionary for this plugin
            prog = self.progress.experiment['plugins'][elm_name]['progress']

            # get the directory (relative to MEDIA ROOT) for storing plots
            directory = os.path.relpath(
                self.config['directory'], start=MEDIA_ROOT
            )

            # create a PLACE plotter for the plugin
            plotter = PlacePlotter(prog, directory)

            # attempt to dynamically import the plugin's Python module
            try:
                plugin = _programmatic_import(
                    python_module_name, python_class_name, plugin_data['config'], plotter)
            except ImportError:
                raise RuntimeError(
                    'Cannot find module related to: {}'.format(plugin_data))
            plugin.priority = plugin_data['priority']
            plugin.elm_module_name = elm_name
            self.plugins.append(plugin)
        # sort plugins based on priority
        self.plugins.sort(key=attrgetter('priority'))

    def config_phase(self):
        """Configure the instruments and post-processing plugins.

        During the configuration phase, instruments and post-processing plugins
        are provided with their configuration data. Metadata is collected from
        all plugins and written to disk.
        """
        self.metadata['directory'] = self.config['directory']

        for plugin in self.plugins:
            if self.abort_event.is_set():
                raise AbortExperiment
            self.progress.log('config', plugin.elm_module_name)
            try:
                config_func = plugin.config
            except AttributeError:
                continue
            config_func(self.metadata, self.config['updates'])

        del self.metadata['directory']
        self.config['metadata'] = self.metadata

        # overwrite the config data now that all plugins have submitted their
        # metadata
        with open(self.config['directory'] + '/config.json', 'w') as config_file:
            json.dump(_remove_specific_items(self.config),
                      config_file, indent=2, sort_keys=True)

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
        self.progress.update_time = 1.0
        for update_number in range(self.config['updates']):
            self._run_update(update_number)
        self.progress.update_time = 0.0

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
            return

        build_single_file(self.config['directory'])
        for plugin in self.plugins:
            if self.abort_event.is_set():
                raise AbortExperiment
            self.progress.log('cleanup', plugin.elm_module_name)
            if issubclass(plugin.__class__, Export):
                plugin.export(self.config['directory'])
            else:
                plugin.cleanup(abort=False)
        with open(self.config['directory'] + '/results.json', 'x') as results_file:
            json.dump(self.progress.to_dict(), results_file,
                      indent=2, sort_keys=True)

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
        then = time()
        self.progress.start_update(update_number)
        data = np.array([(npdatetime64(datetime.datetime.now()),)],
                        dtype=[('PLACE-time', 'datetime64[us]')])
        for plugin in self.plugins:
            if self.abort_event.is_set():
                raise AbortExperiment
            self.progress.log('update', plugin.elm_module_name)
            data = self._run_plugin_update(plugin, update_number, data)

        # save data for this update
        filename = '{}/data_{:03d}.npy'.format(
            self.config['directory'], update_number)
        with open(filename, 'xb') as data_file:
            np.save(data_file, data.copy(), allow_pickle=False)
        now = time()
        update_time = now - then
        weight = max(0.1, 1 / (update_number + 1))
        self.progress.update_time = (
            update_time * weight
            + self.progress.update_time * (1 - weight)
        )

    def _run_plugin_update(self, plugin, update_number, data):
        """Run the update phase on one PLACE plugin"""
        class_ = plugin.__class__
        elm_name = plugin.elm_module_name
        try:
            if issubclass(class_, Instrument):
                new_data = plugin.update(
                    update_number, self.progress.experiment['plugins'][elm_name]['progress'])
                if new_data is not None:
                    data = rfn.merge_arrays([data, new_data], flatten=True)
            elif issubclass(class_, PostProcessing):
                data = plugin.update(update_number, data.copy())
        except RuntimeError as err:
            self.progress.message = str(err)
            self.cleanup_phase(abort=True)
            raise
        return data

    def get_progress(self):
        """Return the progress message"""
        return self.progress.to_dict()

    def abort(self):
        """Tell the experiment to abort"""
        self.progress.log("abort", "none")
        self.abort_event.set()


def _programmatic_import(module_name, class_name, config, plotter):
    """Import a module based on string input.

    This function takes a string for a module and a string for a class and
    imports that class from the given module programmatically.

    :param module_name: the name of the module to import from
    :type module_name: str

    :param class_name: the string of the class to import
    :type class_name: str

    :param config: the JSON configuration data for the module
    :type config: dict

    :param plotter: a PLACE plotting object which is attached to the PLACE
                    progress
    :type plotter: PlacePlotter

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

    # this calls the plugin's __init__() method
    return class_(config, plotter)


def _remove_specific_items(config):
    """removes specific items from the config that should not be saved"""
    # delete author, email, maintainer, and other metadata
    # so they don't appear in the config.json file that is saved
    fixed_config = copy.deepcopy(config)
    for _, plugin in fixed_config['plugins'].items():
        plugin['metadata'].pop('title', None)
        plugin['metadata'].pop('authors', None)
        plugin['metadata'].pop('email', None)
        plugin['metadata'].pop('maintainer', None)
        plugin['metadata'].pop('url', None)
        plugin['metadata'].pop('default_priority', None)
    return fixed_config
