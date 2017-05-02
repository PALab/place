'''
Example usage of TEK_driver module.

@author: Jami L Johnson
Created May 27, 2014
'''

from configparser import ConfigParser
from os.path import expanduser
import numpy as np
import matplotlib.pyplot as plt
from obspy import Trace
from place.automate.tektronix import TEK_driver

def main():
    '''Demonstrate the Tektronix oscilloscope.
    '''

    # get ip address from config file
    config_file = expanduser('~/.place.cfg')
    config = ConfigParser()
    config.read(config_file)
    try:
        ip_addr = config['Tektronix']['ip_address']
    except KeyError:
        if not config.has_section('Tektronix'):
            config.add_section('Tektronix')
        ip_addr = config['Tektronix']['ip_address'] = '130.216.58.218'
        with open(config_file, 'w') as file_out:
            config.write(file_out)

    scope = TEK_driver.TDS3014b(ip_addr=ip_addr)
    header, data = scope.getWaveform(channel=1, format='counts')

    print('connected to: ', scope.getIDN())

    ti_value = float(header['XZERO'])
    tx_value = float(header['XINCR'])
    tf_value = ti_value + (len(data) * tx_value)
    t_value = np.arange(ti_value, tf_value, tx_value)

    # plot data
    plt.plot(t_value, data)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.show()

    # create stream and save in H5 format
    array_data = np.array(data)
    trace = Trace(data=array_data, header=header)
    trace.write('tekfile.h5', 'H5', mode='a')

if __name__ == '__main__':
    main()

