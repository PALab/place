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
import json
from math import ceil, log
from time import sleep
from asyncio import get_event_loop
from os import urandom
from getopt import error as GetOptError
from getopt import getopt
from shlex import split
from websockets.server import serve
from obspy import Trace, UTCDateTime
from obspy.core.trace import Stats
import matplotlib.pyplot as plt

from ..config import PlaceConfig
from ..automate.scan import scan_helpers, scan_functions
from .. import automate
from ..alazartech import atsapi as ats

SCAN_POINT = 1
SCAN_1D = 2
SCAN_2D = 3
SCAN_DUAL = 4
SCAN_POINT_TEST = 5

class ScanFromJSON:
    """An object to describe a scan experiment"""
    def __init__(self):
        self.scan_config = None
        self.scan_type = None
        self.instruments = []

# PUBLIC METHODS
    def config(self, config_string):
        """Configure the scan

        :param config_string: a JSON-formatted configuration
        :type config_string: str
        """
        self.scan_config = json.loads(config_string)
        self.scan_type = self.scan_config['scan_type']
        for instrument_data in self.scan_config['instruments']:
            name = instrument_data['name']
            config = instrument_data['config']
            class_name = getattr(automate, name)
            instrument = class_name()
            instrument.config(json.dumps(config))
            self.instruments.append(instrument)

    def run(self):
        """Perform the scan"""
        if self.scan_type == "scan_point_test":
            for instrument in self.instruments:
                instrument.update()
                instrument.cleanup()
        else:
            raise ValueError('invalid scan type')

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
        if self.par.scan_type == SCAN_POINT:
            self.point()
        elif self.par.scan_type == SCAN_1D:
            self.one_dimension_scan()
        elif self.par.scan_type == SCAN_2D:
            scan_functions.twoD(self.par, self.header)
        elif self.par.scan_type == SCAN_DUAL:
            scan_functions.dual(self.par, self.header)
        else:
            raise ValueError('invalid scan type')

    def point(self):
        """Record a single trace"""
        times = self.par.CONTROL.getTimesOfRecord()
        self.header.delta = times[1]-times[0]
        self.header.starttime = UTCDateTime()
        self.header.x_position = self.par.I1

        if self.par.SOURCE == 'indi':
            laser_check = input('Turn laser on REP? (yes/N) \n')
            if laser_check == 'yes':
                automate.QuantaRay().set('REP')
                sleep(1)
                automate.QuantaRay().getStatus() # keep watchdog happy
            else:
                print('Turning laser off ...')
                automate.QuantaRay().off()
                automate.QuantaRay().closeConnection()
                # add code to close connection to instruments
                exit()

        average, average2 = scan_functions.data_capture(self.par)

        if self.par.PLOT:
            scan_functions.plot(self.header, times, average, self.par)
            if self.par.CHANNEL2 != 'null' and self.par.RECEIVER != 'osldv':
                scan_functions.plot(self.header, times, average2, self.par)
            plt.show()

        self.header.npts = len(average)
        trace = Trace(data=average, header=self.header)
        trace.write(self.par.FILENAME, 'H5', mode='a')

        if self.par.CHANNEL2 != 'null' and self.par.RECEIVER != 'osldv':
            scan_functions.save_trace(self.header, average2, self.par.FILENAME2)
        if self.par.SOURCE == 'indi':
            automate.QuantaRay().set('SING')
            automate.QuantaRay().off()

    def one_dimension_scan(self):
        """Scanning function for 1-stage scanning"""
        times, self.header = scan_functions.get_times(self.par.CONTROL, self.header)
        if self.par.SOURCE == 'indi':
            laser_check = input('Turn laser on REP? (yes/N) \n')
            if laser_check == 'yes':
                automate.QuantaRay().set('REP')
                sleep(1)
                automate.QuantaRay().getStatus() # keep watchdog happy
            else:
                print('Turning laser off ...')
                automate.QuantaRay().off()
                automate.QuantaRay().closeConnection()
                # add code to close connection to instruments
        tracenum = 0
        if self.par.I1 > self.par.F1:
            self.par.D1 = -(self.par.D1)

        x_value = self.par.I1

        if self.par.GROUP_NAME_1 == 'ROT_STAGE':
            pos = self.par.I1
            unit = 'degrees'

        # set up mirrors
        elif self.par.GROUP_NAME_1 in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            theta_step = 1.8e-6 # 1 step = 1.8 urad
            print('Go to starting position for picomotors')
            automate.PMot().Position(self.par.PX, self.par.PY)
            # set position to 'zero'
            automate.PMot().set_DH(self.par.PX)
            automate.PMot().set_DH(self.par.PY)
            if self.par.RECEIVER == 'polytec' or self.par.RECEIVER2 == 'polytec':
                automate.Polytec().autofocusVibrometer(span='Full')
                l_value = self.par.MIRROR_DISTANCE
                unit = 'mm'
            else:
                l_value = self.par.MIRROR_DISTANCE
                unit = 'radians'
            self.par.I1 = float(self.par.I1)/(l_value*theta_step)
            self.par.D1 = float(self.par.D1)/(l_value*theta_step)
            print('group name 1 %s' %self.par.GROUP_NAME_1)
            if self.par.GROUP_NAME_1 == 'PICOMOTOR-X':
                automate.PMot().move_rel(self.par.PX, self.par.I1)
            else:
                automate.PMot().move_rel(self.par.PY, self.par.I1)
        else:
            unit = 'mm'

        # setup plot
        axis_1, axis_2, fig = scan_functions.two_plot(self.par.GROUP_NAME_1, self.header)
        i = 0

        while i < self.par.TOTAL_TRACES_D1:
            if self.par.SOURCE == 'indi':
                automate.QuantaRay().getStatus() # keep watchdog happy
            tracenum += 1
            print('trace ' + tracenum + ' of ' + self.par.TOTAL_TRACES_D1)

            # move stage/mirror
            if self.par.GROUP_NAME_1 in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
    #unused                x_steps = x_value/theta_step
                if self.par.GROUP_NAME_1 == 'PICOMOTOR-X':
                    automate.PMot().move_rel(self.par.PX, self.par.D1)
                    pos = float(automate.PMot().get_TP(self.par.PX))*l_value*theta_step
                elif self.par.GROUP_NAME_1 == 'PICOMOTOR-Y':
                    automate.PMot().move_rel(self.par.PY, self.par.D1)
                    pos = float(automate.PMot().get_TP(self.par.PY))*l_value*theta_step
            else:
                scan_functions.move_stage(self.par.GROUP_NAME_1,
                                          self.par.XPS_1,
                                          self.par.SOCKET_ID_1,
                                          x_value)
                pos = x_value

            scan_functions.update_header(self.header, pos, self.par.GROUP_NAME_1)
            print('position = {} {}'.format(pos, unit))
            sleep(self.par.WAITTIME) # delay after stage movement

            scan_functions.check_vibfocus(self.par.CHANNEL,
                                          self.par.VIB_SIGNAL,
                                          self.par.SIGNAL_LEVEL,
                                          self.par.autofocus)

            average, average2 = scan_functions.data_capture(self.par)

            # save current trace
            scan_functions.save_trace(self.header, average, self.par.FILENAME)

            if self.par.CHANNEL2 != 'null' and self.par.RECEIVER != 'osldv':
                scan_functions.save_trace(self.header, average2, self.par.FILENAME2)

            # update figure
            if self.par.MAP != 'none' and i > 0:
                scan_functions.update_two_plot(times,
                                               average,
                                               x_value,
                                               self.par,
                                               self.header,
                                               fig,
                                               axis_1,
                                               axis_2)
            scan_functions.update_time(self.par)
            x_value += self.par.D1
            i += 1
            if self.par.RETURN == 'True':
                if self.par.GROUP_NAME_1 == 'PICOMOTOR-X':
                    automate.PMot().move_abs(self.par.PX, 0)
                    print('picomotors moved back to zero.')
                elif self.par.GROUP_NAME_1 == 'PICOMOTOR-Y':
                    automate.PMot().move_abs(self.par.PY, 0)
                    print('picomotors moved back to zero.')

        if self.par.SOURCE == 'indi':
            automate.QuantaRay().set('SING')
            automate.QuantaRay().off()
        print('scan complete!')
        print('data saved as: ' + self.par.FILENAME + ' \n')

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
        """Initialize Alazar Oscilloscope Card."""
        # initialize channel for signal from vibrometer decoder
        self.par.CONTROL = automate.TriggeredRecordingController()
        self.par.CONTROL.configureMode = True
        self.par.CONTROL.create_input(self.par.CHANNEL,
                                      self.par.CHANNEL_RANGE,
                                      self.par.AC_COUPLING,
                                      self.par.IMPEDANCE)
        self.par.CONTROL.setSampleRate(self.par.SAMPLE_RATE)
        self.par.SAMPLES = self.par.CONTROL.samplesPerSec*self.par.DURATION*1e-6
        self.par.SAMPLES = int(pow(2, ceil(log(self.par.SAMPLES, 2))))
        self.par.CONTROL.setSamplesPerRecord(samples=self.par.SAMPLES)
        self.par.CONTROL.setRecordsPerCapture(self.par.AVERAGES)
        trigger_level = 128 + int(127 * self.par.TRIG_LEVEL / self.par.TRIG_RANGE)

        print(trigger_level)

        self.par.CONTROL.setTrigger(
            operationType="TRIG_ENGINE_OP_J",
            sourceOfJ=self.par.trigger_source_id_1,
            levelOfJ=trigger_level,
            )
        self.par.CONTROL.setTriggerTimeout(10)
        self.par.CONTROL.configureMode = False

        # FIX THIS
        if self.par.CHANNEL2 != 'null':
            control2 = automate.TriggeredRecordingController()
            control2.configureMode = True
            control2.create_input(
                self.par.CHANNEL2,
                self.par.CHANNEL_RANGE2,
                self.par.AC_COUPLING2,
                self.par.IMPEDANCE2,
                )
            control2.setSampleRate(self.par.SAMPLE_RATE)
    #unused            samples2 = control.samplesPerSec*self.par.DURATION*1e-6
            # round number of samples to next power of two
    #unused            samples2 = int(pow(2, ceil(log(samples, 2))))
            control2.setSamplesPerRecord(samples=self.par.SAMPLES)
            control2.setRecordsPerCapture(self.par.AVERAGES)
            trigger_level = 128 + int(127*self.par.TRIG_LEVEL/self.par.TRIG_RANGE)
            control2.setTrigger(
                operationType="TRIG_ENGINE_OP_J",
                sourceOfJ=self.par.trigger_source_id_1,
                levelOfJ=trigger_level
                )
            control2.setTriggerTimeout(10)
            control2.configureMode = False
            self.par.CONTROL2 = control2

        if self.par.VIB_CHANNEL != 'null':
            # initialize channel for vibrometer sensor head signal
            vib_signal = automate.TriggeredContinuousController()
            vib_signal.configureMode = True
            vib_signal.create_input(
                self.par.VIB_CHANNEL,
                ats.INPUT_RANGE_PM_4_V,
                ats.DC_COUPLING,
                self.par.IMPEDANCE,
                ) # 0 to 3 V DC
            vib_signal.setSamplesPerRecord(samples=1)
            vib_signal.setRecordsPerCapture(3)
            vib_signal.setTrigger(
                operationType="TRIG_ENGINE_OP_J",
                sourceOfJ='TRIG_EXTERNAL',
                levelOfJ=trigger_level,
                )
            vib_signal.setTriggerTimeout(10)
            self.par.VIB_SIGNAL = vib_signal
        else:
            self.par.VIB_SIGNAL = 'null'

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

def main_json():
    """Entry point for a JSON scan.

    JSON scans accept input via the newer JSON method. This is typically not
    called from the command-line.
    """
    scan = ScanFromJSON()
    scan.config(sys.argv[1])
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
