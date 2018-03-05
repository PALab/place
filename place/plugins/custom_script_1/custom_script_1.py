"""PLACE module for running a user specified script"""
import os.path
import subprocess
import numpy as np
from place.plugins.instrument import Instrument

class CustomScript1(Instrument):
    """The custom script class"""
    def __init__(self, config):
        """Initialize the custom script, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self.config_filepath = None
        self.update_filepath = None
        self.cleanup_filepath = None

    def config(self, metadata, total_updates):
        """Validate that the requested scripts exists.

        There is one script each for config, update, and cleanup phases. This
        can be used to test if your code is ready to be put into an official
        PLACE module.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int

        :raises RuntimeError: if a requested script cannot be found
        """
        if self._config['config_script_path'] != '':
            path = self._config['config_script_path']
            self.config_filepath = os.path.abspath(os.path.expanduser(path))
            if not os.path.isfile(self.config_filepath):
                raise RuntimeError(
                    'PLACE cannot find requested config script: {}'.format(self.config_filepath))
            metadata['script1_config_absolute_path'] = self.config_filepath
        if self._config['update_script_path'] != '':
            path = self._config['update_script_path']
            self.update_filepath = os.path.abspath(os.path.expanduser(path))
            if not os.path.isfile(self.update_filepath):
                raise RuntimeError(
                    'PLACE cannot find requested update script: {}'.format(self.update_filepath))
            metadata['script1_update_absolute_path'] = self.update_filepath
        if self._config['cleanup_script_path'] != '':
            path = self._config['cleanup_script_path']
            self.cleanup_filepath = os.path.abspath(os.path.expanduser(path))
            if not os.path.isfile(self.cleanup_filepath):
                raise RuntimeError(
                    'PLACE cannot find requested cleanup script: {}'.format(self.cleanup_filepath))
            metadata['script1_cleanup_absolute_path'] = self.cleanup_filepath

        subprocess.run(['python', self.config_filepath])


    def update(self, update_number):
        """Run the script.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: the exit code of the script
        :rtype: dtype=[('count', 'int16'), ('trace', 'float64', self._samples)])
        """
        complete = subprocess.run(['python', self.update_filepath])
        exit_code_field = '{}-exit_code'.format(self.__class__.__name__)
        test_a = complete.returncode
        test_b = (exit_code_field, 'int64')
        dtype = [test_b]
        return np.array([(test_a,)], dtype=dtype)

    def cleanup(self, abort=False):
        """No action needed at this time.

        :param abort: ``True`` if the experiement is being aborted
        :type abort: bool
        """
        subprocess.run(['python', self.cleanup_filepath])
