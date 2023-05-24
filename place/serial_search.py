"""Functions to search for and identify instruments
connected to serial ports."""

import sys
import glob
import serial
import importlib
import pkgutil

from place.plots import PlacePlotter
from place.config import PlaceConfig
import place.plugins 

def run_search_and_update():
    """Run a serial port serach and update the
    .place.cfg file with the correct ports"""

    print()
    print("PLACE serial search: Running scan for serial ports.")
    instrument_data = get_instruments()
    print("Available ports:", get_available_serial_ports())
    new_instrument_data = query_ports(instrument_data)
    update_place_cfg(new_instrument_data)
    print()
    print("PLACE serial search: Scan complete.")
    print()


def get_available_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM{}'.format(i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def get_instruments():
    """Find the instruments in the .place.cfg file
    that need serial ports. Returns a list, where
    each element contains the instrument name, current
    port, instrument class, and the name of the port
    field in the config file. More than one entry can
    exist per instrument class. """

    cfg = PlaceConfig()
    instruments = list([key for key in cfg.keys()])
    if 'DEFAULT' in instruments:
        instruments.remove('DEFAULT')
    if 'Django' in instruments:
        instruments.remove('Django')

    instrument_data = []
    for ints in instruments:
        instrument_keys = cfg.get_section_keys(ints)
        for key in instrument_keys:
            if 'port' in key:
                _class = get_instrument_class(ints)
                port_field_name = key
                port = cfg.query_config_value(ints, port_field_name)
                if _class is not None:
                    instrument_data.append([ints,port,_class,port_field_name])

    return instrument_data


def get_instrument_class(name):
    """Find and return the Instrument class called name"""

    for _, submodule_name, _ in pkgutil.walk_packages(place.plugins .__path__):
        full_module_name = f"place.plugins.{submodule_name}"

        try:
            submodule = importlib.import_module(full_module_name)
        except:
            continue

        if hasattr(submodule, name):
            class_ = getattr(submodule, name)
            return class_
    else:
        print("Class not found: {}.".format(name))


def query_ports(instrument_data):
    """Query whether the instrument is connected to the port"""

    possible_ports = get_available_serial_ports()

    for i, data_list in enumerate(instrument_data):
        class_name = data_list[0]   
        print()
        print("Querying", class_name)
        _class = data_list[2]({}, PlacePlotter({}, "."))
        try:
            query_function = _class.serial_port_query
        except AttributeError:
            print("Serial Search: Could not find serial_port_query function in {} class.".format(class_name))
            continue
        for port in possible_ports:
            print("Testing port:", port)
            try:
                correct_port = query_function(port, data_list[3])
            except Exception as e:
                #raise(e)
                continue
            if correct_port:
                possible_ports.remove(port)
                data_list[1] = port
                instrument_data[i] = data_list
                print("Success! {0} {1} is (probably) {2}".format(class_name,data_list[3],port))
                break

    return instrument_data

def update_place_cfg(instrument_data):
    """Update the .place.cfg file with the 
    discovered ports."""

    cfg = PlaceConfig()

    for data_list in instrument_data:
        inst_name = data_list[0]
        port_field_name = data_list[3]
        port_value = data_list[1]
        cfg.set_config_value(inst_name, port_field_name, port_value)


if __name__ == '__main__':
    run_search_and_update()
