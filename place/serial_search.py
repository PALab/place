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

    print("PLACE serial search: Running scan for serial ports.")
    serial_dict = get_instruments()
    print("Available ports:", get_available_serial_ports())
    print(serial_dict)
    new_serial_dict = query_ports(serial_dict)
    print(new_serial_dict)
    update_place_cfg(new_serial_dict)
    print("PLACE serial search: Scan complete.")


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
    that need serial ports. Returns a dictionary
    of instrument:port pairs"""

    cfg = PlaceConfig()
    instruments = list([key for key in cfg.keys()])
    if 'DEFAULT' in instruments:
        instruments.remove('DEFAULT')
    if 'Django' in instruments:
        instruments.remove('Django')

    serial_ints = []
    instrument_data = []
    for ints in instruments:
        port_field_name = 'port'
        port = cfg.query_config_value(ints, 'port')
        if port == "":
            port_field_name = 'serial_port'
            port = cfg.query_config_value(ints, 'serial_port')
        if port == "":
            continue

        _class = get_instrument_class(ints)
        if _class is not None:
            serial_ints.append(ints)
            instrument_data.append([port,_class,port_field_name])


    serial_dict = dict(zip(serial_ints, instrument_data))

    return serial_dict


def get_instrument_class(name):
    """Find and return the Instrument class called name"""

    for _, submodule_name, _ in pkgutil.walk_packages(place.plugins .__path__):
        full_module_name = f"place.plugins.{submodule_name}"

        try:
            submodule = importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            continue

        if hasattr(submodule, name):
            class_ = getattr(submodule, name)
            return class_
    else:
        print("Class not found: {}.".format(name))


def query_ports(serial_dict):
    """Query whether the instrument is connected to the port"""

    possible_ports = get_available_serial_ports()

    for (class_name, data) in serial_dict.items():
        print()
        print("Querying", class_name)
        _class = data[1]({}, PlacePlotter({}, "."))
        try:
            query_function = _class.serial_port_query
        except AttributeError:
            print("Serial Search: Could not find serial_port_query function in {} class.".format(class_name))
            continue
        for port in possible_ports:
            print("Port",port,len(port))
            if query_function(port):
                possible_ports.remove(port)
                data[0] = port
                serial_dict[class_name] = data
                break

    return serial_dict

def update_place_cfg(serial_dict):
    """Update the .place.cfg file with the 
    discovered ports."""

    cfg = PlaceConfig()

    for (inst_name, data) in serial_dict.items():
        port_field_name = data[2]
        port_value = data[0]
        cfg.set_config_value(inst_name, port_field_name, port_value)


if __name__ == '__main__':
    run_search_and_update()
