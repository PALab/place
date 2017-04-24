"""Master script to run laser-ultrasound experiment using PLACE automation.

#. Instruments and scan parameters are initialized
#. Header is created
#. Scan: data is acquired, displayed, and appended to stream file for
   each stage position

   - Data is saved to an HDF5 file (e.g. filename.h5) in the same folder
     as Scan.py:

#. Connection to instruments are closed

@author: Jami L Johnson
March 19, 2015
"""
import sys
import signal
from os import urandom
from getopt import error as getopterror
from getopt import getopt
from shlex import split

from ..config import PlaceConfig
from ..automate.scan import scan_helpers
from ..automate.scan import scan_functions

def main(args_in=None):
    """Main"""
    instruments = []
    par = []
    if args_in is None:
        args_in = sys.argv
    try:
        process_args(args_in)
    except KeyboardInterrupt:
        print('Keyboard Interrupt!  Instrument connections closing...')
        scan_functions.close(instruments, par)

def process_args(args_in):
    """Process command line options"""
    try:
        opts, _ = getopt(args_in[1:], 'h', [
            'help', 's1=', 's2=', 'scan=', 'dm=', 'sr=',
            'tm=', 'ch=', 'ch2=', 'av=', 'wt=', 'rv=',
            'ret=', 'sl=', 'vch=', 'tl=', 'tr=', 'cr=',
            'cr2=', 'cp=', 'cp2=', 'ohm=', 'ohm2=',
            'i1=', 'd1=', 'f1=', 'i2=', 'd2=', 'f2=',
            'n=', 'n2=', 'dd=', 'rg=', 'map=', 'en=',
            'lm=', 'rr=', 'pp=', 'bp=', 'so=', 'comments='])

    except getopterror as msg:
        print(msg)
        print('for help use --help')
        sys.exit(1)

    par = scan_helpers.options(opts)
    if par is None:
        return

    # -----------------------------------------------------
    # Initialize instruments
    # -----------------------------------------------------

    instruments = []

    config = PlaceConfig()
    picomotor_ip = config.get_config_value(
        'XPS',
        'picomotor controller IP address',
        '130.216.58.155',
        )
    other_ip = config.get_config_value(
        'XPS',
        'other controller IP address',
        '130.216.58.154',
        )

    # Initialize stage or mirrors for each dimension
    if par['SCAN'] == '1D':
        if par['GROUP_NAME_1'] == 'PICOMOTOR-X' or par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
            par = scan_helpers.picomotor_controller(picomotor_ip, 23, par)
        else:
            par = scan_helpers.controller(other_ip, par, 1)
        instruments.append(par['GROUP_NAME_1'])

    elif par['SCAN'] == '2D' or par['SCAN'] == 'dual':
        if par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            par = scan_helpers.picomotor_controller(picomotor_ip, 23, par)
        else:
            par = scan_helpers.controller(other_ip, par, 1)
        instruments.append(par['GROUP_NAME_1'])
        if par['GROUP_NAME_2'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            par = scan_helpers.picomotor_controller(picomotor_ip, 23, par)
        else:
            par = scan_helpers.controller(other_ip, par, 2)
        print(par['GROUP_NAME_2'])
        instruments.append(par['GROUP_NAME_2'])

    # Initialize and set header information for receiver
    receiver = par['RECEIVER']
    if receiver == 'polytec':
        par = scan_helpers.polytec(par)
        instruments.append('POLYTEC')
    elif receiver == 'gclad':
        par['MAX_FREQ'] = '6MHz'
        par['MIN_FREQ'] = '50kHz'
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = '1'
        par['CALIB_UNIT'] = 'V'
    elif receiver == 'osldv':
        par['MAX_FREQ'] = ''
        par['MIN_FREQ'] = ''
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = ''
        par['CALIB_UNIT'] = 'V'
    elif receiver == 'none':
        par['MAX_FREQ'] = ''
        par['MIN_FREQ'] = ''
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = ''
        par['CALIB_UNIT'] = ''

    # Initialize oscilloscope card
    par = scan_helpers.osci_card(par)

    # Initialize Quanta-Ray source laser
    if par['SOURCE'] == 'indi':
        instruments.append('INDI')
        laser_check = input(
            'You have chosen to control the INDI laser with PLACE.'
            + 'Do you wish to continue? (yes/N) \n')
        if laser_check == 'yes':
            scan_functions.quanta_ray(par['ENERGY'], par)
        else:
            print('Stopping scan ... ')
            scan_functions.close(instruments, par)
    par = scan_helpers.scan_time(par)

    # -----------------------------------------------------
    # Initialize header
    # -----------------------------------------------------

    header = scan_functions.header(par)

    # -----------------------------------------------------
    # Perform scan
    # -----------------------------------------------------

    scan_type = par['SCAN']
    if scan_type == '1D':
        scan_functions.oneD(par, header)
    elif scan_type == '2D':
        scan_functions.twoD(par, header)
    elif scan_type == 'point':
        scan_functions.point(par, header)
    elif scan_type == 'dual':
        scan_functions.dual(par, header)
    else:
        print('invalid scan type!')

    # -----------------------------------------------------
    # close instrument connections
    # -----------------------------------------------------
    scan_functions.close(instruments, par)

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
    import websockets
    import asyncio

    def ask_exit():
        """Signal handler to catch ctrl-c (SIGINT) or SIGTERM"""
        loop.stop()

    async def scan_socket(websocket, _):
        """Creates an asyncronous websocket to listen for scans."""
        key = secure_random()
        print("Starting websockets server on port {}".format(port))
        print("The key for this session is {0:04d}".format(key))
        sys.stdout.flush()
        # get a scan command from the webapp
        request = await websocket.recv()
        split_args = split(request)
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
    """Generate a random key number.

    Returns a number between 0000-9999
    """
    # This can be replaced by the `secret` library in Python 3.6
    total = 0
    for num in urandom(100):
        total = total + num
    return total % 10000


if __name__ == "__main__":
    print("This script should not be executed directly.")
    print("Please use `place_scan` instead of calling this file.")
    print("For help, please run:\n")
    print("    place_scan --help")
    sys.exit(0)
