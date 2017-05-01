"""This module allows interfacing with Polytec vibrometer OFV-5000
controller and OFV-505 sensor head. Functions based on Polytec
"RS-232 Interface Commands: OFV-5000 User Manual"

**NOTE** For each polytec controller, different decoders may be
installed. The number assigned to each decoder may also vary,
therefore the decoder functions may need to be modified accordingly.

Example Usage:

::

     from place.automate.polytec.vibrometer import Polytec

     # initialize serial port
     Polytec(portPolytec='/dev/ttyS0', baudPolytec=115200)

     # set range of decoder:
     Polytec().setRange('VD-09', '5mm/s/V')

     # turn off echo:
     Polytec().set_attr(ECHO_INTERFACE_0, 'Off')

     # perform a full-range autofocus:
     Polytec().autofocusVibrometer(span='Full')

     # obtain the maximum frequency for vibrometer VD-09:
     range = Polytec().getMaxFreq(decoder='VD-09')
     print(range)

     # reset controller processor:
     Polytec().reset_processor()


@author: Jami L. Johnson
April 14, 2014
"""
from time import sleep
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS

from ...config import PlaceConfig
from ..instrument import Instrument

# Message constant string values
BAUD_INTERFACE_0 = ',Interface,0,BaudRate'
ECHO_INTERFACE_0 = ',Interface,0,Echo'
FOCUS_SENSORHEAD_0 = ',SensorHead,0,Focus'
FOCUS_AUTO_SENSORHEAD_0 = ',SensorHead,0,AutoFocus'
FOCUS_AUTO_AREA_SENSORHEAD_0 = ',SensorHead,0,AutoFocusArea'
FOCUS_AUTO_RESULT_SENSORHEAD_0 = ',SensorHead,0,AutoFocusResult'
FOCUS_AUTO_SPAN_SENSORHEAD_0 = ',SensorHead,0,AutoFocusSpan'
FOCUS_MANUAL_SENSORHEAD_0 = ',SensorHead,0,ManualFocus'
FOCUS_REMOTE_SENSORHEAD_0 = ',SensorHead,0,RemoteFocus'
NAME_CONTROLLER_0 = ',Controller,0,Name'
NAME_INTERFACE_0 = ',Interface,0,Name'
NAME_SENSORHEAD_0 = ',SensorHead,0,Name'
POWERUP_CONTROLLER_0 = ',Controller,0,PowerUp'
REMOTE_CONTROLLER_0 = ',Controller,0,Remote'
VERSION_CONTROLLER_0 = ',Controller,0,Version'
VERSION_SENSORHEAD_0 = ',SensorHead,0,Version'

DEV_BAUD_INTERFACE_0 = 'DevInfo,Interface,0,BaudRate'
DEV_ECHO_INTERFACE_0 = 'DevInfo,Interface,0,Echo'
DEV_FOCUS_SENSORHEAD_0 = 'DevInfo,SensorHead,0,Focus'
DEV_FOCUS_AUTO_SENSORHEAD_0 = 'DevInfo,SensorHead,0,AutoFocus'
DEV_FOCUS_AUTO_AREA_SENSORHEAD_0 = 'DevInfo,SensorHead,0,AutoFocusArea'
DEV_FOCUS_AUTO_RESULT_SENSORHEAD_0 = 'DevInfo,SensorHead,0,AutoFocusResult'
DEV_FOCUS_AUTO_SPAN_SENSORHEAD_0 = 'DevInfo,SensorHead,0,AutoFocusSpan'
DEV_FOCUS_MANUAL_SENSORHEAD_0 = 'DevInfo,SensorHead,0,ManualFocus'
DEV_FOCUS_REMOTE_SENSORHEAD_0 = 'DevInfo,SensorHead,0,RemoteFocus'
DEV_NAME_CONTROLLER_0 = 'DevInfo,Controller,0,Name'
DEV_NAME_INTERFACE_0 = 'DevInfo,Interface,0,Name'
DEV_NAME_SENSORHEAD_0 = 'DevInfo,SensorHead,0,Name'
DEV_POWERUP_CONTROLLER_0 = 'DevInfo,Controller,0,PowerUp'
DEV_REMOTE_CONTROLLER_0 = 'DevInfo,Controller,0,Remote'
DEV_VERSION_CONTROLLER_0 = 'DevInfo,Controller,0,Version'
DEV_VERSION_SENSORHEAD_0 = 'DevInfo,SensorHead,0,Version'

class Polytec(Instrument):
    """Polytec driver"""
    def __init__(self, portPolytec=None, baudPolytec=115200):
        """Define settings for RS-232 serial port"""

        if not portPolytec:
            # get serial port from config file
            config = PlaceConfig()
            portPolytec = config.get_config_value('Polytec', 'port', default='/dev/ttyS0')

        self.serial = Serial(
            port=portPolytec,
            baudrate=baudPolytec,
            parity=PARITY_NONE,
            stopbits=STOPBITS_ONE,
            bytesize=EIGHTBITS
            )

    def openConnection(self):
        """Open RS-232 serial connection to Polytec serial port"""
        self.serial.close()
        self.serial.open()
        polytec_open = self.serial.isOpen()
        if polytec_open:
            self.serial.write('GetDevInfo,Controller,0,Name\n'.encode())
            print('connected to ' + self.serial.readline().decode())
        else:
            print('ERROR: unable to connect to vibrometer')
            raise IOError

    def closeConnection(self):
        """Closes RS-232 serial connection with vibrometer"""
        self.serial.close()
        print('serial connection to vibrometer closed')

    def write_and_readline(self, string):
        """ writes a line to the serial port and reads the one-line response """
        self.serial.write(string.encode())
        return self.serial.readline().decode()

    def cleanup(self):
        """Perform cleanup tasks for this device"""
        self.closeConnection()

    def get_attr(self, msg):
        """Helper method used to get messages from the controller

        The message should be one of the constants specifying the information
        to be read.
        """
        if msg == FOCUS_SENSORHEAD_0:
            # update status before setting focus
            self.serial.write('Set,SensorHead,0,StatusUpdate\n'.encode())
        return self.write_and_readline('Get' + msg + '\n')

    def set_attr(self, msg, value, verify=True):
        """Helper method used to set values in the controller

        The message should be one of the constants specifying the information
        to be set. The value should be the value it should be set to.
        """
        self.serial.write(('Set' + msg + ',' + value + '\n').encode())
        if verify is True and self.get_attr('Get' + msg + '\n') != value:
            print('failed to set attribute value')
            raise IOError

    def reset_processor(self):
        """Reset the processor of the controller"""
        self.serial.write('Set,Controller,0,Reset,1\n'.encode())
        print('waiting 10 seconds for controller processor to reset')
        sleep(10)
        print('processor reset')

    def status_update(self):
        """Set status of the sensor head"""
        return self.write_and_readline('Set,SensorHead,0,StatusUpdate,1\n')

    def autofocusVibrometer(self, span='Full'):
        """Autofocuses the vibrometer depending on chosen span (Full, Medium, Small)"""
        print('autofocusing vibrometer...')
        self.set_attr(FOCUS_AUTO_SPAN_SENSORHEAD_0, span, verify=False)
        self.set_attr(FOCUS_AUTO_SENSORHEAD_0, 'Search', verify=False)
        for _ in range(30):
            sleep(1)
            focus_answer = self.get_attr(FOCUS_AUTO_RESULT_SENSORHEAD_0)
            if focus_answer == 'Found\n':
                break
        else:
            print('autofocus failed')
            raise IOError
        print('autofocus ' + focus_answer)

    def get_dev_name(self, decoder='DD-300'):
        """Returns either the name of the displacement decoder or "not Installed"
        if the decoder is not installed
        """
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Name\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Name\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,Name\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,Name\n')
        else:
            raise IOError

    def get_dev_range(self, decoder='DD-300'):
        """Returns all possible measurement ranges for the decoder with physical
        units. "Not Available" returned if decoder not installed
        """
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Range\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Range\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,Range\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,Range\n')
        else:
            raise IOError

    def get_dev_resolution(self, decoder='DD-300'):
        """Returns all possible resolution with physical units for the selected
        decoder, or "Not Available returned if decoder is not installed.
        """
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Resolution\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Resolution\n')
        else:
            print('ERROR: resolution only available for displacement decoders')
            raise IOError

    def get_dev_max_freq(self, decoder='DD-300'):
        """Returns all possible maximum frequencies with physical units for the
        selected decoder, or "Not Available" if decoder is not installed
        """
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,MaxFreq\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,MaxFreq\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,MaxFreq\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,MaxFreq\n')
        else:
            raise IOError

    def get_dev_delay(self, decoder='DD-300'):
        """Returns all measurement ranges with physical units for the selected
        decoder, or "Not Available" if decoder is not installed
        """
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,SignalDelay\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,SignalDelay\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,SignalDelay\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,SignalDelay\n')
        else:
            raise IOError

    def get_name(self, decoder='DD-300'):
        """Returns the name of the decoder, e.g. DD-300"""
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Name\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Name\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,Name\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,Name\n')
        else:
            raise IOError

    def get_range(self, decoder='DD-300'):
        """Returns current measurement range with physical units, e.g.
        125mm/s/V
        """
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Range\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Range\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,Range\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,Range\n')
        else:
            raise IOError

    def get_resolution(self, decoder='DD-300'):
        """Get resolution of decoder

        Returns resolution with unit of selected decoder, e.g. 5120 nm.  Only
        valid for displacement decoers
        """
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Resolution\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Resolution\n')
        else:
            print('ERROR: resolution only available for displacement decoders')
            raise IOError

    def getMaxFreq(self, decoder='DD-300'):
        """Get maximum frequency of decoder

        Returns maximum frequency of the selected decoder with unit for current
        range of decoder, e.g. 20MHz.
        """
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,MaxFreq\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,MaxFreq\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,MaxFreq\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,MaxFreq\n')
        else:
            raise IOError

    def getDelay(self, decoder='DD-300'):
        """Get transit time delay

        Returns (typical) signal transit time delay for the selected decoder
        with units, e.g. 8.16 us
        """
        if decoder == 'DD-300':
            return '0 us'
        elif decoder == 'DD-900':
            return '0 us'
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,SignalDelay\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,SignalDelay\n')
        else:
            raise IOError

    def setRange(self, decoder='DD-300', drange='5mm/s/V'):
        """setRange"""
        if decoder == 'DD-300':
            self.serial.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,DisplDec,0,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'DD-900':
            self.serial.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,DisplDec,1,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-09':
            self.serial.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,VeloDec,1,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-08':
            self.serial.write(('Set,VeloDec,0,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,0,Range\n')
            thename = self.write_and_readline('Get,VeloDec,0,Name\n')
            print('decoder: ' + thename)
            print('range of VD-08 set to: ' + therange)
