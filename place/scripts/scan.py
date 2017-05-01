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
from asyncio import get_event_loop
from os import urandom
from getopt import error as GetOptError
from getopt import getopt
from shlex import split
from websockets.server import serve
from obspy.core.trace import Stats

from ..config import PlaceConfig
from ..automate.scan import scan_helpers, scan_functions
from .. import automate

SCAN_POINT = 1
SCAN_1D = 2
SCAN_2D = 3
SCAN_DUAL = 4

class Scan:
    """An object to describe a scan experiment"""
    def __init__(self, opts):
        """Constructor arguments

        :param opts: the option/value pairs returned from getopt()
        :type opts: list
        """
        self.par = scan_helpers.options(opts)
        self.header = None
        self.instruments = []
        self._init_stages()
        self._init_receiver()
        self._init_oscilloscope()
        if self.par.SOURCE == 'indi':
            self._init_indi()
        self._scan_time()
        self._init_header()

# PUBLIC METHODS
    def run(self):
        """Perform scan"""
        if self.par.scan_type == SCAN_1D:
            scan_functions.oneD(self.par, self.header)
        elif self.par.scan_type == SCAN_2D:
            scan_functions.twoD(self.par, self.header)
        elif self.par.scan_type == SCAN_POINT:
            scan_functions.point(self.par, self.header)
        elif self.par.scan_type == SCAN_DUAL:
            scan_functions.dual(self.par, self.header)
        else:
            raise ValueError('invalid scan type')

    def cleanup(self):
        """Close connections and complete scan"""
        for device in self.instruments:
            if device in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
                automate.PMot().close()
            elif (self.par.DIMENSIONS == 1 and
                  device in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']):
                self.par.XPS_1.TCP__CloseSocket(self.par.SOCKET_ID_1)
                print('Connection to {} closed'.format(self.par.GROUP_NAME_1))
            elif (self.par.DIMENSIONS == 2 and
                  device in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']):
                self.par.XPS_2.TCP__CloseSocket(self.par.SOCKET_ID_2)
                print('Connection to {} closed'.format(self.par.GROUP_NAME_2))
            else:
                device.cleanup()

# PRIVATE METHODS
    def _init_stages(self):
        """Initialize stage or mirrors for each dimension"""
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
        if self.par.scan_type == SCAN_1D:
            if (self.par.GROUP_NAME_1 == 'PICOMOTOR-X'
                    or self.par.GROUP_NAME_1 == 'PICOMOTOR-Y'):
                self.par = scan_helpers.picomotor_controller(picomotor_ip, 23, self.par)
            else:
                self.par = scan_helpers.controller(other_ip, self.par, 1)
            self.instruments.append(self.par.GROUP_NAME_1)

        elif self.par.scan_type == SCAN_2D or self.par.scan_type == SCAN_DUAL:
            if self.par.GROUP_NAME_1 in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
                self.par = scan_helpers.picomotor_controller(picomotor_ip, 23, self.par)
            else:
                self.par = scan_helpers.controller(other_ip, self.par, 1)
            self.instruments.append(self.par.GROUP_NAME_1)
            if self.par.GROUP_NAME_2 in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
                self.par = scan_helpers.picomotor_controller(picomotor_ip, 23, self.par)
            else:
                self.par = scan_helpers.controller(other_ip, self.par, 2)
            print(self.par.GROUP_NAME_2)
            self.instruments.append(self.par.GROUP_NAME_2)

    def _init_receiver(self):
        """Initialize and set header information for receiver"""
        receiver = self.par.RECEIVER
        if receiver == 'polytec':
            self.par = scan_helpers.polytec(self.par)
            self.instruments.append('POLYTEC')
        elif receiver == 'gclad':
            self.par.MAX_FREQ = '6MHz'
            self.par.MIN_FREQ = '50kHz'
            self.par.TIME_DELAY = 0
            self.par.DECODER = ''
            self.par.DECODER_RANGE = ''
            self.par.CALIB = '1'
            self.par.CALIB_UNIT = 'V'
        elif receiver == 'osldv':
            self.par.MAX_FREQ = ''
            self.par.MIN_FREQ = ''
            self.par.TIME_DELAY = 0
            self.par.DECODER = ''
            self.par.DECODER_RANGE = ''
            self.par.CALIB = ''
            self.par.CALIB_UNIT = 'V'
        elif receiver == 'none':
            self.par.MAX_FREQ = ''
            self.par.MIN_FREQ = ''
            self.par.TIME_DELAY = 0
            self.par.DECODER = ''
            self.par.DECODER_RANGE = ''
            self.par.CALIB = ''
            self.par.CALIB_UNIT = ''

    def _init_oscilloscope(self):
        """Initialize oscilloscope card"""
        self.par = scan_helpers.osci_card(self.par)

    def _init_indi(self):
        """Initialize Quanta-Ray source laser"""
        qray = automate.QuantaRay()
        self.instruments.append(qray)
        laser_check = input(
            'You have chosen to control the INDI laser with PLACE.'
            + 'Do you wish to continue? (yes/N) \n')
        if laser_check == 'yes':
            scan_functions.quanta_ray(qray, self.par.ENERGY, self.par)
        else:
            print('Stopping scan ... ')
            self.cleanup()

    def _scan_time(self):
        """scan the time"""
        self.par = scan_helpers.scan_time(self.par)

    def _init_header(self):
        """Initialize generic trace header for all traces

        The header is a Stats object from the obspy module.
        """
        self.header = Stats()
        if self.par.IMPEDANCE == 1:
            self.header.impedance = '1Mohm'
        else:
            self.header.impedance = '50 ohms'
        if self.par.IMPEDANCE2 == 1:
            self.header.impedance2 = '1Mohm'
        else:
            self.header.impedance2 = '50 ohms'
        self.header.x_position = self.par.I1
        self.header.max_frequency = self.par.MAX_FREQ
        self.header.receiver = self.par.RECEIVER
        self.header.decoder = self.par.DECODER
        self.header.decoder_range = self.par.DECODER_RANGE
        self.header.source_energy = self.par.ENERGY
        self.header.wavelength = self.par.WAVELENGTH
        self.header.x_unit = 'mm'
        self.header.theta_unit = 'deg'
        self.header.y_unit = 'mm'
        self.header.comments = self.par.COMMENTS
        self.header.averages = self.par.AVERAGES
        self.header.calib_unit = self.par.CALIB_UNIT
        self.header.time_delay = self.par.TIME_DELAY
        self.header.scan_time = ''
        self.header.focus = 0
        if self.par.RECEIVER == 'polytec':
            if self.par.DECODER == 'DD-300' and self.par.IMPEDANCE == 1:
                self.header.calib = 25
            else:
                self.header.calib = self.par.CALIB
        self.header.channel = self.par.CHANNEL

def main(args_in=None):
    """Entry point to a scan.

    If arguments are provided, it will use these. Otherwise, it will use
    sys.argv.

    :param args_in: arguments to use for the scan
    :type args_in: list

    :raises ValueError: when parameters are not parsed
    :raiser error: when getopt fails
    """
    if args_in is None:
        args_in = sys.argv
    try:
        opts, unused = getopt(args_in[1:], 'h', [
            'help', 's1=', 's2=', 'scan=', 'dm=', 'sr=',
            'tm=', 'ch=', 'ch2=', 'av=', 'wt=', 'rv=',
            'ret=', 'sl=', 'vch=', 'trigger_source_id_1=', 'tl=', 'tr=', 'cr=',
            'cr2=', 'cp=', 'cp2=', 'ohm=', 'ohm2=',
            'i1=', 'd1=', 'f1=', 'i2=', 'd2=', 'f2=',
            'n=', 'n2=', 'dd=', 'rg=', 'map=', 'en=',
            'lm=', 'rr=', 'pp=', 'bp=', 'so=', 'autofocus=', 'comments='])
    except GetOptError as msg:
        print(msg)
        print('for help use --help')
        sys.exit(1)
    if unused != []:
        raise ValueError("Some scan arguments have been ignored. "
                         "Please check your parameters.")
    scan = Scan(opts)
    scan.run()

# wait for requests
def scan_server(port=9130):
    """Starts a websocket server to listen for scan requests.

    This function is used to initiate a special scan process. Rather
    than specify the parameters via the command-line, this mode waits
    for scan commands to arrive via a websocket.

    Once this server is started, it will need to be killed via ctrl-c or
    similar.

    """
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
            main(split_args)
            await websocket.send("Scan received")
        else:
            print("Kay invalid. Scan cancelled.")
            await websocket.send("Invalid key")

    loop = get_event_loop()
    # set up signal handlers
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), ask_exit)
    coroutine = serve(scan_socket, 'localhost', port)
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
