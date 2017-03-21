'''
Master script to run laser-ultrasound experiment using PLACE automation.

#. Instruments and scan parameters are initialized
#. Header is created
#. Scan: data is acquired, displayed, and appended to stream file for
   each stage position

   - Data is saved to an HDF5 file (e.g. filename.h5) in the same folder
     as Scan.py:

#. Connection to instruments are closed

@author: Jami L Johnson
March 19, 2015
'''
from __future__ import print_function

import sys
import os
import time
from math import ceil, log
import signal
import getopt
import re
import shlex
import functools

# set permissions of RS-232 serial port for vibrometer control
# (removed in favour of using proper permissions -Paul Freeman)
#os.system('sudo chmod -R 0777 /dev/ttyS0')
#os.system('sudo chmod a+rw /dev/ttyS0')

# set permissions of USB port for laser source
#os.system('sudo chmod -R 0777 /dev/ttyUSB0') # laser
#os.system('sudo chmod a+rw /dev/ttyUSB0')

import matplotlib.pyplot as plt
import numpy as np
from numpy import matrix
from obspy import read, Trace, UTCDateTime
from obspy.core.trace import Stats
from obspy.core import AttribDict
import h5py

# PLACE modules
try:
    import place.automate.osci_card.controller as card
except OSError:
    print('Warning: Alazar library (LibATSapi.so) not found')
from place.automate.xps_control.XPS_C8_drivers import XPS
from place.automate.new_focus.picomotor import PMot
try:
    from place.automate.new_focus.Calibrate import Position, getInverse, get_distance # TODO why does this file not exist in repo?
except ImportError:
    pass
from place.automate.quanta_ray.QRay_driver import QuantaRay
from place.automate.scan.scanFunctions import Initialize, Execute, Scan

# pickle library
try:
    # import C optimzed library if possible
    import cPickle as pickle
except ImportError:
    # fall back to Python implementation
    import pickle

global instruments, par
instruments = []
par = []

def main(args_in=sys.argv):
    try:
        process_args(args_in)
    except KeyboardInterrupt:
        print('Keyboard Interrupt!  Instrument connections closing...')
        Execute().close(instruments,par)

def process_args(args_in):
    # -----------------------------------------------------
    # process command line options
    # -----------------------------------------------------
    try:
        opts,args = getopt.getopt(args_in[1:], 'h',['help','s1=','s2=','scan=','dm=','sr=','tm=','ch=','ch2=','av=','wt=','rv=','ret=','sl=','vch=','tl=','tr=','cr=','cr2=','cp=','cp2=','ohm=','ohm2=','i1=','d1=','f1=','i2=','d2=','f2=','n=','n2=','dd=','rg=','map=','en=','lm=','rr=','pp=','bp=','so=','comments='])

    except getopt.error as msg:
        print(msg)
        print('for help use --help')
        sys.exit(1)

    par = Initialize().options(opts, args)
    if par == None:
        return

    # -----------------------------------------------------
    # Initialize instruments
    # -----------------------------------------------------

    instruments = []

    # Initialize stage or mirrors for each dimension

    if par['SCAN'] == '1D':
        if par['GROUP_NAME_1'] == 'PICOMOTOR-X' or par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
            par = Initialize().picomotor_controller('130.216.58.155',23,par)

        else:
            par = Initialize().controller('130.216.58.154',par,1)
        instruments.append(par['GROUP_NAME_1'])

    elif par['SCAN'] == '2D' or par['SCAN'] == 'dual':
        if par['GROUP_NAME_1'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
            par = Initialize().picomotor_controller('130.216.58.155',23,par)
        else:
            par = Initialize().controller('130.216.58.154',par,1)
        instruments.append(par['GROUP_NAME_1'])
        if par['GROUP_NAME_2'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
            par = Initialize().picomotor_controller('130.216.58.155',23,par)
        else:
            par = Initialize().controller('130.216.58.154',par,2)
        print(par['GROUP_NAME_2'])
        instruments.append(par['GROUP_NAME_2'])

    # Initialize and set header information for receiver
    if par['RECEIVER'] == 'polytec':
        par = Initialize().polytec(par)
        instruments.append('POLYTEC')
    elif par['RECEIVER'] == 'gclad':
        par['MAX_FREQ'] = '6MHz'
        par['MIN_FREQ'] = '50kHz'
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = '1'
        par['CALIB_UNIT'] = 'V'
    elif par['RECEIVER'] == 'osldv':
        par['MAX_FREQ'] = ''
        par['MIN_FREQ'] = ''
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = ''
        par['CALIB_UNIT'] = 'V'
    elif par['RECEIVER'] == 'none':
        par['MAX_FREQ'] = ''
        par['MIN_FREQ'] = ''
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = ''
        par['CALIB_UNIT'] = ''

    # Initialize oscilloscope card
    par = Initialize().osci_card(par)

    # Initialize Quanta-Ray source laser
    if par['SOURCE'] == 'indi':
        instruments.append('INDI')
        laser_check = raw_input('You have chosen to control the INDI laser with PLACE. Do you wish to continue? (yes/N) \n')
        if laser_check == 'yes':
            traceTime = Initialize().quanta_ray(par['ENERGY'], par)
        else:
            print('Stopping scan ... ')
            Execute().close(instruments, par)
    par = Initialize().time(par)

    # -----------------------------------------------------
    # Initialize header
    # -----------------------------------------------------

    header = Initialize().header(par)

    # -----------------------------------------------------
    # Perform scan
    # -----------------------------------------------------

    if par['SCAN'] == '1D':
        Scan().oneD(par, header)
    elif par['SCAN'] == '2D':
        Scan().twoD(par, header)
    elif par['SCAN'] == 'point':
        Scan().point(par,header)
    elif par['SCAN'] == 'dual':
        Scan().dual(par,header)
    else:
        print('invalid scan type!')

    # -----------------------------------------------------
    # close instrument connections
    # -----------------------------------------------------
    Execute().close(instruments,par)

    sys.exit(0)



# wait for requests
def scan_server(port=9130):
    """Starts a websocket server to listen for scan requests.

    This function is used to initiate a special scan process. Rather
    than specify the parameters via the command-line, this mode waits
    for scan commands to arrive via a websocket.

    Once this server is started, it will need to be killed via ctrl-c or
    similar.

    """
    try:
        import websockets
    except ImportError:
        print("Running as server requires the websockets module")
        print("but websockets cannot be imported.")
        print()
        print("Installing websockets can be as simple as:")
        print()
        print("    pip install websockets")
        print()
        sys.exit(1)
    try:
        import asyncio
    except ImportError:
        print("Running as server requires the asyncio module")
        print("but asyncio cannot be imported.")
        print()
        sys.exit(1)

    def ask_exit():
        """Signal handler to catch ctrl-c (SIGINT) or SIGTERM"""
        loop.stop()

    async def scan_socket(websocket, path):
        """Creates an asyncronous websocket to listen for scans."""
        key = secure_random()
        print("Starting websockets server on port {}".format(port))
        print("The key for this session is {0:04d}".format(key))
        sys.stdout.flush()
        # get a scan command from the webapp
        request = await websocket.recv()
        split_args = shlex.split(request)
        print("This is what received:")
        print(request)
        if key == int(split_args.pop(0)):
            print("Kay valid. Starting scan.")
            process_args(split_args)
            await websocket.send("Scan received")
        else:
            print("Kay invalid. Scan cancelled.")
            await websocket.send("Invalid key")

    loop = asyncio.get_event_loop()
    # set up signal handlers
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), ask_exit)
    coroutine = websockets.server.serve(scan_socket, 'localhost', port)
    # run websocket server
    server = loop.run_until_complete(coroutine)
    loop.run_forever()
    # cleanup
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

def secure_random():
    """Generate a random key number
    
    Returns a number between 0000-9999"""
    # TODO This can be replaced by the `secret` library
    # coming out in Python 3.6
    s = 0
    for x in os.urandom(100):
        s = s + x
    return s % 10000


if __name__ == "__main__":
    print("This script should not be executed directly.")
    print("Please use `place_scan` instead of calling this file.")
    print("For help, please run:\n")
    print("    place_scan --help")
    sys.exit(0)

