"""New scan file for PLACE 0.3
"""
import sys
import json
from importlib import import_module

class Scan3:
    """An object to describe a scan experiment"""
    def __init__(self):
        self.scan_config = None
        self.scan_type = None
        self.instruments = []

    def config(self, config_string):
        """Configure the scan

        :param config_string: a JSON-formatted configuration
        :type config_string: str
        """
        self.scan_config = json.loads(config_string)
        self.scan_type = self.scan_config['scan_type']
        for instrument_data in self.scan_config['instruments']:
            module_name = instrument_data['module_name']
            class_name = instrument_data['class_name']
            config = instrument_data['config']

            module = import_module('place.plugins.' + module_name)
            class_name = getattr(module, class_name)
            instrument = class_name()
            instrument.config(json.dumps(config))
            self.instruments.append(instrument)

    def run(self):
        """Perform the scan"""
        if self.scan_type == "scan_point_test":
            for instrument in self.instruments:
                instrument.update()
                instrument.cleanup()
        else:
            raise ValueError('invalid scan type')

def main():
    """Entry point for a 0.3 scan."""
    scan = Scan3()
    scan.config(sys.argv[1])
    scan.run()
