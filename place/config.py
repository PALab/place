'''A module for working with the PLACE config file ('~/.place.cfg').
'''
from os.path import expanduser
from configparser import ConfigParser

# pylint: disable=too-many-ancestors
class PlaceConfig(ConfigParser):
    '''
    Class object for handling values in the PLACE config file.
    '''

    __path = expanduser('~/.place.cfg')

    def __init__(self):
        super(PlaceConfig, self).__init__()
        self.read(PlaceConfig.__path)

    def get_config_value(self, section, name, default=None):
        '''
        Gets a value from the configuration.
        '''
        try:
            return self[section][name]
        except KeyError:
            if default is not None:
                self.set_config_value(section, name, default)
            return default

    def set_config_value(self, section, name, value):
        '''
        Sets a value in the config file and saves the file.
        '''
        if not self.has_section(section):
            self.add_section(section)
        self[section][name] = value
        with open(PlaceConfig.__path, 'w') as file_out:
            self.write(file_out)
