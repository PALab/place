"""Functions to search for and identify instruments
connected to serial ports"""

import sys
import glob
import serial
import importlib
import pkgutil

from place.plots import PlacePlotter
from place.config import PlaceConfig
import place.plugins 


def get_available_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
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
        port = cfg.query_config_value(ints, 'port')
        if port == "":
            port = cfg.query_config_value(ints, 'serial_port')
        if port == "":
            continue

        _class = get_instrument_class(ints)
        if _class is not None:
            serial_ints.append(ints)
            instrument_data.append((port,_class))


    serial_dict = dict(zip(serial_ints, instrument_data))

    return serial_dict


def get_instrument_class(name):
    """Find and return the Instrument class called name"""

    for _, submodule_name, _ in pkgutil.walk_packages(place.plugins .__path__):
        full_module_name = f"place.plugins.{submodule_name}"

        try:
            submodule = importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            print("didn't find a module")
            continue

        if hasattr(submodule, name):
            class_ = getattr(submodule, name)
            return class_
    else:
        print("Class not found: {}.".format(name))


def query_ports(serial_dict):
    """Query whether the instrument is connected to the port"""

    possible_ports = get_available_serial_ports()

    instruments, ports = [], []

    for (class_name, data) in serial_dict.items():
        _class = data[1]({}, PlacePlotter({}, "."))
        for port in possible_ports:
            if _class.serial_port_query(port):
                possible_ports.remove(port)
                instruments.append(class_name)
                ports.append(port)
                break
        
    confirmed_ports_dict = dict(zip(instruments, ports))

    return confirmed_ports_dict

if __name__ == '__main__':
    print(get_available_serial_ports())
    serial_dict = get_instruments()
    print(serial_dict)
    print(query_ports(serial_dict))
