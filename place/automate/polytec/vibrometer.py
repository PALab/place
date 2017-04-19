'''
This module allows interfacing with Polytec vibrometer OFV-5000
controller and OFV-505 sensor head. Functions based on Polytec
"RS-232 Interface Commands: OFV-5000 User Manual"

**NOTE** For each polytec controller, different decoders may be
installed. The number assigned to each decoder may also vary,
therefore the decoder functions may need to be modified accordingly.

Example Usage:

::

     from place.automate.polytec.vibrometer import Polytec

     # initialize serial port
     Polytec(portPolytec='/dev/ttyS0',baudPolytec=115200)

     # set range of decoder:
     Polytec().setRange('VD-09','5mm/s/V')

     # turn off echo:
     Polytec().setEcho(echo='Off'):

     # perform a full-range autofocus:
     Polytec().autofocusVibrometer(span='Full')

     # obtain the maximum frequency for vibrometer VD-09:
     range = Polytec().getMaxFreq(decoder='VD-09')
     print range

     # reset controller processor:
     Polytec().resetProcessor()


@author: Jami L. Johnson
April 14, 2014
'''
from __future__ import print_function

import time
from serial import Serial
import serial

from place.config import PlaceConfig

class Polytec(Serial): # pylint: disable=too-many-ancestors
    ''' Polytec driver '''
    def __init__(self, portPolytec=None, baudPolytec=115200):
        '''Define settings for RS-232 serial port'''

        if not portPolytec:
            # get serial port from config file
            config = PlaceConfig()
            portPolytec = config.get_config_value('Polytec', 'port', default='/dev/ttyS0')

        super(Polytec, self).__init__(
            port=portPolytec,
            baudrate=baudPolytec,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            )

    def openConnection(self):
        '''Open RS-232 serial connection to Polytec serial port'''
        self.close()
        self.open()
        polytec_open = self.isOpen()
        if polytec_open:
            self.write('GetDevInfo,Controller,0,Name\n'.encode())
            print('connected to', self.readline().decode())
        else:
            print('ERROR: unable to connect to vibrometer')
            exit()

    def closeConnection(self):
        '''Closes RS-232 serial connection with vibrometer'''
        self.close()
        print('serial connection to vibrometer closed')

# Message constant string values
BAUD_INTERFACE_0 = 'Get,Interface,0,BaudRate\n'
ECHO_INTERFACE_0 = 'Get,Interface,0,Echo\n'
FOCUS_SENSORHEAD_0 = 'Get,SensorHead,0,Focus\n'
FOCUS_AUTO_AREA_SENSORHEAD_0 = 'Get,SensorHead,0,AutoFocusArea\n'
FOCUS_AUTO_RESULT_SENSORHEAD_0 = 'Get,SensorHead,0,AutoFocusResult\n'
FOCUS_AUTO_SPAN_SENSORHEAD_0 = 'Get,SensorHead,0,AutoFocusSpan\n'
FOCUS_MANUAL_SENSORHEAD_0 = 'Get,SensorHead,0,ManualFocus\n'
FOCUS_REMOTE_SENSORHEAD_0 = 'Get,SensorHead,0,RemoteFocus\n'
NAME_CONTROLLER_0 = 'Get,Controller,0,Name\n'
NAME_INTERFACE_0 = 'Get,Interface,0,Name\n'
NAME_SENSORHEAD_0 = 'Get,SensorHead,0,Name\n'
POWERUP_CONTROLLER_0 = 'Get,Controller,0,PowerUp\n'
REMOTE_CONTROLLER_0 = 'Get,Controller,0,Remote\n'
VERSION_CONTROLLER_0 = 'Get,Controller,0,Version\n'
VERSION_SENSORHEAD_0 = 'Get,SensorHead,0,Version\n'

DEV_BAUD_INTERFACE_0 = 'GetDevInfo,Interface,0,BaudRate\n'
DEV_ECHO_INTERFACE_0 = 'GetDevInfo,Interface,0,Echo\n'
DEV_FOCUS_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,Focus\n'
DEV_FOCUS_AUTO_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,AutoFocus\n'
DEV_FOCUS_AUTO_AREA_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,AutoFocusArea\n'
DEV_FOCUS_AUTO_RESULT_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,AutoFocusResult\n'
DEV_FOCUS_AUTO_SPAN_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,AutoFocusSpan\n'
DEV_FOCUS_MANUAL_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,ManualFocus\n'
DEV_FOCUS_REMOTE_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,RemoteFocus\n'
DEV_NAME_CONTROLLER_0 = 'GetDevInfo,Controller,0,Name\n'
DEV_NAME_INTERFACE_0 = 'GetDevInfo,Interface,0,Name\n'
DEV_NAME_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,Name\n'
DEV_POWERUP_CONTROLLER_0 = 'GetDevInfo,Controller,0,PowerUp\n'
DEV_REMOTE_CONTROLLER_0 = 'GetDevInfo,Controller,0,Remote\n'
DEV_VERSION_CONTROLLER_0 = 'GetDevInfo,Controller,0,Version\n'
DEV_VERSION_SENSORHEAD_0 = 'GetDevInfo,SensorHead,0,Version\n'

class PolytecController(Polytec): # pylint: disable=too-many-ancestors
    '''PolytecController class'''

    def write_and_readline(self, string):
        ''' writes a line to the serial port and reads the one-line response '''
        self.write(string.encode())
        return self.readline().decode()

    def get_attr(self, msg):
        '''
        Helper method used to get messages from the controller

        The message should be one of the constants specifying the information
        to be read.
        '''
        if msg == FOCUS_SENSORHEAD_0:
            # update status before setting focus
            self.write('Set,SensorHead,0,StatusUpdate\n'.encode())
        return self.write_and_readline(msg)

    def resetProcessor(self):
        '''Reset the processor of the controller'''
        self.write('Set,Controller,0,Reset,1\n'.encode())
        time.sleep(10)
        print('processor reset')

    def setPowerup(self, powerup='Last'):
        '''Set the name for saving and loading the settings, e.g. Default (refer to controller manual'''
        powerup = powerup+'\n'
        self.write(('Set,Controller,0,PowerUp,' + powerup).encode())
        self.write('Get,Controller,0,PowerUp\n'.encode())
        check = self.readline().decode()
        if check == powerup:
            print('power up changed to: ', check)
        else:
            print('failed to change power up')
            exit()

    def setRemote(self, remote='Local'):
        '''Set the status of the controller'''
        remote += '\n'
        self.write(('Set,Controller,0,Remote,'+remote).encode())
        self.write('Get,Controller,0,Remote\n'.encode())
        check = self.readline().decode()
        if check == remote:
            print('remote changed to: ', check)
        else:
            print('ERROR: failed to change remote')
            exit()

    def setEcho(self, echo='Off'):
        '''
        Set the echo fuction On/Off. NOTE: turning echo 'On' can cause problems
        communicating with polytec.
        '''
        echo += '\n'
        self.write(('Set,Interface,0,Echo,'+echo).encode())
        self.write('Get,Interface,0,Echo\n'.encode())
        check = self.readline().decode()
        if check == echo:
            print('echo turned: ', check)
        else:
            print('ERROR: unable to change echo.')
            exit()

    def setBaud(self, baud=115200): #check baud rate??
        '''
        Set the baud rate for the RS-232 interface. NOTE: this does NOT
        change the baudrate of the serial port. If baudrate of interface is
        changed, may cause communication issues with serial port.
        '''
        baud = str(baud) + '\n'
        self.write(('Set,Interface,0,BaudRate,'+baud).encode())
        self.write('Get,Interface,0,BaudRate\n'.encode())
        check = self.readline().decode()
        if check == baud:
            print('baud rate changed to: ', check)
        else:
            print('ERROR: unable to change baud rate.')
            exit()

    def setStatusUpdate(self):
        '''Set status of the sensor head'''
        return self.write_and_readline('Set,SensorHead,0,StatusUpdate,1\n')

    def setFocusRange(self, focusRange):#TEST THIS
        '''Set focus range of the sensor head '''
        focusRange = str(focusRange) + '\n'
        self.write(('Set,SensorHead,0,Focus'+focusRange).encode())
        check = self.get_attr(DEV_FOCUS_SENSORHEAD_0)
        if check == focusRange:
            pass
        else:
            print('ERROR: Unable to change focus range')
            exit()
        return self.readline().decode()

    def setManualFocus(self, lock):
        '''Set the status of the manual focus on the sensor head, e.g. 'Unlocked' '''
        lock += '\n'
        self.write(('Set,SensorHead,0,ManualFocus'+lock).encode('utf-8'))
        check = self.get_attr(FOCUS_MANUAL_SENSORHEAD_0)
        if check == lock:
            pass
        else:
            print('ERROR: Unable to change status of manual focus')
            exit()

    def setRemoteFocus(self, remoteFocus):
        '''Sets the status of the remote focus on the sensor head'''
        remoteFocus += '\n'
        self.write(('Set,SensorHead,0,RemoteFocus'+remoteFocus).encode('utf-8'))
        check = self.get_attr(FOCUS_REMOTE_SENSORHEAD_0)
        if check == remoteFocus:
            pass
        else:
            print('ERROR: unable to set the remote focus of the sensor head')
            exit()

    def setAutoFocusArea(self, focusArea):
        '''Sets the area for the autofocus'''
        focusArea = str(focusArea) + '\n'
        self.write(('Set,SensorHead,AutoFocusArea'+focusArea).encode('utf-8'))
        check = self.get_attr(FOCUS_AUTO_AREA_SENSORHEAD_0)
        if check == focusArea:
            pass
        else:
            print('ERROR: Unable to set autofocus area')
            exit()

    def autofocusVibrometer(self, span='Full'):
        '''Autofocuses the vibrometer depending on chosen span (Full, Medium, Small)'''
        print('autofocusing vibrometer...')
        self.write(('Set,SensorHead,0,AutoFocusSpan,'+span+'\n').encode())
        self.write('Set,SensorHead,0,AutoFocus,Search\n'.encode())
        time.sleep(1)
        focusAnswer = self.write_and_readline('Get,SensorHead,0,AutoFocusResult\n')
        i = 0
        while focusAnswer != 'Found\n':
            focusAnswer = self.write_and_readline('Get,SensorHead,0,AutoFocusResult\n')
            time.sleep(1)
            if i > 30:
                break
            i += 1
        print('autofocus', focusAnswer)

    def getDevName(self, decoder='DD-300'):
        '''
        Returns either the name of the displacement decoder or "not Installed"
        if the decoder is not installed
        '''
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Name\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Name\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,Name\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,Name\n')
        return None

    def getDevRange(self, decoder='DD-300'):
        '''
        Returns all possible measurement ranges for the decoder with physical
        units. "Not Available" returned if decoder not installed
        '''
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Range\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Range\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,Range\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,Range\n')
        return None

    def getDevResolution(self, decoder='DD-300'):
        '''
        Returns all possible resolution with physical units for the selected
        decoder, or "Not Available returned if decoder is not installed.
        '''
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,Resolution\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,Resolution\n')
        elif decoder == 'VD-09':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        elif decoder == 'VD-08':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        return None

    def getDevMaxFreq(self, decoder='DD-300'):
        '''
        Returns all possible maximum frequencies with physical units for the
        selected decoder, or "Not Available" if decoder is not installed
        '''
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,MaxFreq\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,MaxFreq\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,MaxFreq\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,MaxFreq\n')
        return None

    def getDevDelay(self, decoder='DD-300'):
        '''
        Returns all measurement ranges with physical units for the selected
        decoder, or "Not Available" if decoder is not installed
        '''
        if decoder == 'DD-300':
            return self.write_and_readline('GetDevInfo,DisplDec,0,SignalDelay\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('GetDevInfo,DisplDec,1,SignalDelay\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('GetDevInfo,VeloDec,1,SignalDelay\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('GetDevInfo,VeloDec,0,SignalDelay\n')
        return None

    def getName(self, decoder='DD-300'):
        '''Returns the name of the decoder, e.g. DD-300'''
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Name\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Name\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,Name\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,Name\n')
        return None

    def getRange(self, decoder='DD-300'):
        '''Returns current measurement range with physical units, e.g. 125mm/s/V'''
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Range\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Range\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,Range\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,Range\n')
        return None

    def getResolution(self, decoder='DD-300'):
        '''Returns resolution with unit of selected decoder, e.g. 5120 nm.  Only valid for displacement decoers'''
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,Resolution\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,Resolution\n')
        elif decoder == 'VD-09':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        elif decoder == 'VD-08':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        return None

    def getMaxFreq(self, decoder='DD-300'):
        '''Returns maximum frequency of the selected decoder with unit for current range of decoder, e.g. 20MHz.'''
        if decoder == 'DD-300':
            return self.write_and_readline('Get,DisplDec,0,MaxFreq\n')
        elif decoder == 'DD-900':
            return self.write_and_readline('Get,DisplDec,1,MaxFreq\n')
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,MaxFreq\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,MaxFreq\n')
        return None

    def getDelay(self, decoder='DD-300'):
        '''Returns (typical) signal transit time delay for the selected decoder with units, e.g. 8.16 us'''
        if decoder == 'DD-300':
            return '0 us'
        elif decoder == 'DD-900':
            return '0 us'
        elif decoder == 'VD-09':
            return self.write_and_readline('Get,VeloDec,1,SignalDelay\n')
        elif decoder == 'VD-08':
            return self.write_and_readline('Get,VeloDec,0,SignalDelay\n')
        return None

    def setRange(self, decoder='DD-300', drange='5mm/s/V'):
        '''setRange'''
        if decoder == 'DD-300':
            self.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,DisplDec,0,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'DD-900':
            self.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,DisplDec,1,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-09':
            self.write(('Set,VeloDec,1,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,1,Range\n')
            thename = self.write_and_readline('Get,VeloDec,1,Name\n')
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-08':
            self.write(('Set,VeloDec,0,Range,' + drange + '\n').encode())
            therange = self.write_and_readline('Get,VeloDec,0,Range\n')
            thename = self.write_and_readline('Get,VeloDec,0,Name\n')
            print('decoder: ' + thename)
            print('range of VD-08 set to: ' + therange)
