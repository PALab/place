"""Run an experiment"""
import os
import json
from operator import attrgetter
from importlib import import_module
import numpy as np
from numpy.lib import recfunctions as rfn
from .plugins.instrument import Instrument
from .plugins.postprocessing import PostProcessing
from .plugins.export import Export

class BasicExperiment:
    """Basic experiment class"""
    def __init__(self, config):
        """Experiment constructor

        :param config: a decoded JSON dictionary
        :type config: dict
        """
        self.config = config
        self.modules = []
        self.metadata = {'comments': self.config['comments']}
        self._create_experiment_directory()
        self.init_phase()

    def run(self):
        """Run the experiment."""
        self.config_phase()
        self.update_phase()
        self.cleanup_phase(abort=False)

    def init_phase(self):
        """Initialize the modules.

        During this phase, all modules receive their configuration data and
        should store it. The list of modules being used by the experiment is
        created and sorted by their priority level. No physical configuration
        should occur during this phase.
        """
        for module in self.config['modules']:
            module_name = module['module_name']
            class_string = module['class_name']
            priority = module['priority']
            config = module['config']

            postprocessor = _programmatic_import(module_name, class_string, config)
            postprocessor.priority = priority
            self.modules.append(postprocessor)

        # sort modules based on priority
        self.modules.sort(key=attrgetter('priority'))

    def config_phase(self):
        """Configure the instruments and post-processing modules.

        During the configuration phase, instruments and post-processing modules
        are provided with their configuration data. Metadata is collected from
        all modules and written to disk.
        """
        for module in self.modules:
            print("...configuring {}...".format(module.__class__.__name__))
            module.config(self.metadata, self.config['updates'])
        with open(self.config['directory'] + '/meta.json', 'x') as meta_file:
            json.dump(self.metadata, meta_file, indent=2)

    def update_phase(self):
        """Perform all the updates on the modules.

        The update phase occurs N times, based on the user configuration for
        the experiment. This function loops over the instruments and
        post-processing modules (based on their priority) and calls their
        update method.

        One file will be written for each update.
        """
        for update_number in range(self.config['updates']):
            current_data = np.array([(np.datetime64('now'),)], dtype=[('time', 'datetime64[us]')])

            for module in self.modules:
                class_ = module.__class__
                print("...{}: updating {}...".format(update_number,
                                                     module.__class__.__name__))
                if issubclass(class_, Instrument):
                    try:
                        module_data = module.update(update_number)
                    except RuntimeError:
                        self.cleanup_phase(abort=True)
                        raise
                    if module_data is not None:
                        current_data = rfn.merge_arrays([current_data, module_data],
                                                        flatten=True)
                elif issubclass(class_, PostProcessing):
                    current_data = module.update(update_number, current_data.copy())
            filename = '{}/scan_data_{:03d}.npy'.format(self.config['directory'], update_number)
            with open(filename, 'xb') as data_file:
                np.save(data_file, current_data.copy(), allow_pickle=False)


    def cleanup_phase(self, abort=False):
        """Cleanup the moduless.

        During this phase, each module has its cleanup method called. If the
        abort flag has not been set in the cleanup call, this will be passed to
        the module.

        :param abort: signals that the experiment is being aborted
        :type abort: bool
        """
        if abort:
            for module in self.modules:
                print("...aborting {}...".format(module.__class__.__name__))
                module.cleanup(abort=True)
        else:
            for module in self.modules:
                class_ = module.__class__
                if issubclass(class_, Export):
                    print("...exporting with {}...".format(module.__class__.__name__))
                else:
                    print("...cleaning up {}...".format(module.__class__.__name__))
                    module.cleanup(abort=False)

    def _create_experiment_directory(self):
        self.config['directory'] = os.path.normpath(self.config['directory'])
        if not os.path.exists(self.config['directory']):
            os.makedirs(self.config['directory'])
        else:
            for i in range(1, 1000):
                if not os.path.exists(self.config['directory'] + '-' + str(i)):
                    self.config['directory'] += '-' + str(i)
                    break
            print('Experiment path exists - saving to ' + self.config['directory'])
            os.makedirs(self.config['directory'])
        with open(self.config['directory'] + '/config.json', 'x') as config_file:
            json.dump(self.config, config_file, indent=2)

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
