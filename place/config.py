'''A module for working with the PLACE config file ('~/.place.cfg').
'''
from os.path import expanduser
from configparser import ConfigParser

def get_config_value(section, name, default):
    '''
    Gets a value from the config file.

    This method opens the PLACE config file and looks for a
    value in a given secton. If it exists, it is returned.
    If it does not exist, the default value passed to the
    fucntion is stored in the config file and returned to
    the user.
    '''
    # get picomotor IP address from config file
    config_file = expanduser('~/.place.cfg')
    config = ConfigParser()
    config.read(config_file)
    try:
        return config[section][name]
    except KeyError:
        if not config.has_section(section):
            config.add_section(section)
        config[section][name] = default
        with open(config_file, 'w') as file_out:
            config.write(file_out)
        return default


