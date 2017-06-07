"""Basic scan"""
import os
import json
from operator import attrgetter
from importlib import import_module
import numpy as np
from numpy.lib import recfunctions as rfn
from .plugins.instrument import Instrument

class BasicScan:
    """Basic scan class"""
    def __init__(self, config, socket=None):
        """scan constructor

        :param config: a decoded JSON dictionary
        :type config: dict

        :param socket: a socket connected to the webapp for mpld3 data
        :type socket: websocket
        """
        self.config = config
        self.socket = socket
        self.instruments = []
        self.metadata = {'comments': self.config['comments']}
        self._create_experiment_directory()
        self.init_phase()

    def run(self):
        """Run the scan."""
        self.config_phase()
        self.update_phase()
        self.cleanup_phase(abort=False)

    def init_phase(self):
        """Initialize the instruments.

        During this phase, all instruments receive their configuration data and
        should store it. The list of instruments being used by the scan is created
        and sorted by their priority level. No physical configuration should occur
        during this phase.
        """
        for instrument_data in self.config['instruments']:
            module_name = instrument_data['module_name']
            class_string = instrument_data['class_name']
            priority = instrument_data['priority']
            config = instrument_data['config']

            instrument = _programmatic_import(module_name, class_string, config)
            instrument.priority = priority
            self.instruments.append(instrument)

        # sort instruments based on priority
        self.instruments.sort(key=attrgetter('priority'))

    def config_phase(self):
        """Configure the instruments.

        During the configuration phase, instruments are provided with their
        configuration data. Metadata is collected from all instruments and
        written to disk.
        """
        for instrument in self.instruments:
            print("...configuring {}...".format(instrument.__class__.__name__))
            instrument.config(self.metadata, self.config['updates'])
        with open(self.config['directory'] + '/meta.json', 'x') as meta_file:
            json.dump(self.metadata, meta_file, indent=2)

    def update_phase(self):
        """Perform all the updates on the instruments.

        The update phase occurs N times, based on the user configuration for the
        scan. This function loops over the instruments (based on their priority)
        and calls their update method.

        On the first update, PLACE will retrieve the receive the first set of
        data from all the instruments. Based on this data, it will construct
        the record array to be used for the rest of the scan. On each of the
        following updates, PLACE will simply record the data returned from each
        instrument.
        """
        data = np.recarray((1,), dtype=[('update', int)])
        data[0] = (0,)

        for update_number in range(self.config['updates']):
            if update_number == 0:
                for instrument in self.instruments:
                    print("...{}: updating {}...".format(update_number,
                                                         instrument.__class__.__name__))
                    new_data = instrument.update(update_number, self.socket)
                    if new_data is not None:
                        data = rfn.rec_append_fields(
                            data,
                            new_data.dtype.names,
                            [new_data[col] for col in new_data.dtype.names],
                            dtypes=[new_data.dtype[i] for i in range(len(new_data.dtype))])
                data = data.copy()
                data.resize((self.config['updates'],))
            else:
                for instrument in self.instruments:
                    print("...{}: updating {}...".format(update_number,
                                                         instrument.__class__.__name__))
                    new_data = instrument.update(update_number, self.socket)
                    if new_data is not None:
                        for name in new_data.dtype.names:
                            data[update_number][name] = new_data[name]
        with open(self.config['directory'] + '/data.npy', 'xb') as data_file:
            np.save(data_file, data)

    def cleanup_phase(self, abort=False):
        """Cleanup the instruments.

        During this phase, each instrument has its cleanup method called. If the
        abort flag has not been set in the cleanup call, this will be passed to the
        instrument.

        :param abort: signals that a scan is being aborted
        :type abort: bool
        """
        if abort:
            for instrument in self.instruments:
                print("...aborting {}...".format(instrument.__class__.__name__))
                instrument.cleanup(abort=True)
        else:
            for instrument in self.instruments:
                print("...cleaning up {}...".format(instrument.__class__.__name__))
                instrument.cleanup(abort=False)

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
    """Import an instrument based on string input.

    This function takes a string for a module and a string for a class and
    imports that class from the given module programmatically. It then creates
    and instance of that class and ensures it is a subclass of Instrument.

    :param module_name: the name of the module to import from
    :type module_name: str

    :param class_name: the string of the class to import
    :type class_name: str

    :param config: the JSON configuration data for the instrument
    :type config: dict

    :returns: an instance of the instrument matching the class and module
    :rtype: Instrument

    :raises TypeError: if requested instrument has not been subclassed correctly
    """
    module = import_module('place.plugins.' + module_name)
    class_ = getattr(module, class_name)
    if not issubclass(class_, Instrument):
        raise TypeError(class_name + " is not a subclass of Instrument")
    return class_(config)
