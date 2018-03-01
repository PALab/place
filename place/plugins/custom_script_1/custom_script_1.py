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
        self.filepath = None

    def config(self, metadata, total_updates):
        """Validate that the requested script exists.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int

        :raises RuntimeError: if the requested script cannot be found
        """
        self.filepath = os.path.abspath(os.path.expanduser(self._config['script_path']))
        if not os.path.isfile(self.filepath):
            raise RuntimeError('PLACE cannot find requested script: {}'.format(self.filepath))
        metadata['script1_absolute_path'] = self.filepath

    def update(self, update_number):
        """Run the script.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: the exit code of the script
        :rtype: dtype=[('count', 'int16'), ('trace', 'float64', self._samples)])
        """
        complete = subprocess.run(['python', self.filepath])
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
        pass
