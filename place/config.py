"""A module for working with the PLACE config file ('.place.cfg')"""
from os.path import expanduser
from configparser import ConfigParser
import inspect

class PlaceConfigError(ValueError):
    """Error returned if there is a bad value in ~/.place.cfg file."""
    pass

# pylint: disable=too-many-ancestors
class PlaceConfig(ConfigParser):
    """Class object for handling values in the PLACE config file."""

    __path = expanduser('~/.place.cfg')

    def __init__(self):
        super(PlaceConfig, self).__init__()
        self.read(PlaceConfig.__path)

    def get_config_value(self, section, name, default=None):
        """Gets a value from the configuration file.

        :param section: the name of the section heading under which the value
                        will be found in the config file. Typically this should
                        be the class name (i.e. `self.__class__.__name__`)
                        although this is not enforced.
        :type section: str

        :param name: the name (or key) under which the value is stored in the
                     config file
        :type name: str

        :param default: (optional) a default value can be specified, which will
                        be saved into the config file and used if another value
                        does not exist in the config file
        :type default: str

        :returns: the value from the configuration file
        :rtype: str

        :raises ValueError: if value does not exist in the config file and no
                            default is specified *(note that the value will be
                            added to config file with a value of
                            'fix_this_value')*
        """
        fix_me = "fix_this_value"
        try:
            value = self[section][name]
        except KeyError:
            if default is not None:
                self.set_config_value(section, name, default)
                value = default
            else:
                self.set_config_value(section, name, fix_me)
                raise PlaceConfigError(name + " not found for " + section
                                       + ". Please add this value to "
                                       + PlaceConfig.__path)
        if value == fix_me:
            raise PlaceConfigError(name + " not found for " + section
                                   + ". Please add this value to "
                                   + PlaceConfig.__path)
        return value

    def set_config_value(self, section, name, value):
        """Sets a value in the config file and saves the file.

        Typically, this should not be used by PLACE modules. Config values
        should be updated by the end-user by manually editing the config file.
        """
        if not self.has_section(section):
            self.add_section(section)
        self[section][name] = value
        with open(PlaceConfig.__path, 'w') as file_out:
            self.write(file_out)


    def query_config_value(self, section, name):
        """Same as get_config_value, except it does not set
        a new value if the value is not found

        :param section: the name of the section heading under which the value
                        will be found in the config file. Typically this should
                        be the class name (i.e. `self.__class__.__name__`)
                        although this is not enforced.
        :type section: str

        :param name: the name (or key) under which the value is stored in the
                     config file
        :type name: str

        :returns: the value from the configuration file (empty string
                  if not found)
        :rtype: str
        """
        
        try:
            value = self[section][name]
        except KeyError:
            value = ""

        return value

    def get_section_keys(self, section):
        """Get a list of all the config value keys under
        the heading section.

        :param section: the name of the section heading under which the value
                        will be found in the config file. 
        :type section: str

        :returns: a list of keys (may be empty)
        :rtype: list
        """
        
        try:
            keys = list(self[section].keys())
        except KeyError:
            keys = []

        return keys
    

    