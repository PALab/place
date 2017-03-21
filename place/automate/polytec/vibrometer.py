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
import serial

class Polytec:
    '''Polytec class'''
    def __init__(self, portPolytec='/dev/ttyS0', baudPolytec=115200):
        '''Define settings for RS-232 serial port'''
        self.ser = serial.Serial(
            port=portPolytec,
            baudrate=baudPolytec,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            )
    def openConnection(self):
        '''Open RS-232 serial connection to Polytec serial port'''
        self.ser.close()
        self.ser.open()
        polytecOpen = self.ser.isOpen()
        if polytecOpen == True:
            self.ser.write('GetDevInfo,Controller,0,Name\n'.encode('utf-8'))
            print('connected to', self.ser.readline())
        else:
            print('ERROR: unable to connect to vibrometer')
            exit()

    def closeConnection(self):
        '''Closes RS-232 serial connection with vibrometer'''
        self.ser.close()
        print('serial connection to vibrometer closed')

class PolytecController(Polytec):
    '''PolytecController class'''

    def getDevName(self):
        '''Returns all possible controllers'''
        self.ser.write('GetDevInfo,Controller,0,Name\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevVersion(self):
        '''Returns all possible controller versions'''
        self.ser.write('GetDevInfo,Controller,0,Version\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevPowerup(self):
        '''Returns all possible names for saving and loading the settings'''
        self.ser.write('GetDevInfo,Controller,0,PowerUp\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevRemote(self):
        '''Returns all possible status of the controller'''
        self.ser.write('GetDevInfo,Controller,0,Remote\n'.encode('utf-8'))
        return self.ser.readline()

    def getName(self):
        '''Returns current controller name'''
        self.ser.write('Get,Controller,0,Name\n'.encode('utf-8'))
        return self.ser.readline()

    def getVersion(self):
        '''Returns current controller version'''
        self.ser.write('Get,Controller,0,Version\n'.encode('utf-8'))
        return self.ser.readline()

    def getPowerup(self):
        '''Returns current controller name for saving and loading the settings'''
        self.ser.write('Get,Controller,0,PowerUp\n'.encode('utf-8'))
        currentPowerup = self.ser.readline()
        return currentPowerup

    def getRemote(self):
        '''Returns status of the controller'''
        self.ser.write('Get,Controller,0,Remote\n'.encode('utf-8'))
        return self.ser.readline()

    def setPowerup(self, powerup='Last'):
        '''Set the name for saving and loading the settings, e.g. Default (refer to controller manual'''
        powerup = powerup+'\n'
        self.ser.write(('Set,Controller,0,PowerUp,' + powerup).encode('utf-8'))
        self.ser.write('Get,Controller,0,PowerUp\n'.encode('utf-8'))
        check = self.ser.readline()
        if check == powerup:
            print('power up changed to: ', check)
        else:
            print('failed to change power up')
            exit()

    def setRemote(self, remote='Local'):
        '''Set the status of the controller'''
        remote += '\n'
        self.ser.write(('Set,Controller,0,Remote,'+remote).encode('utf-8'))
        self.ser.write('Get,Controller,0,Remote\n'.encode('utf-8'))
        check = self.ser.readline()
        if check == remote:
            print('remote changed to: ', check)
        else:
            print('ERROR: failed to change remote')
            exit()

    def resetProcessor(self):
        '''Reset the processor of the controller'''
        self.ser.write('Set,Controller,0,Reset,1\n'.encode('utf-8'))
        time.sleep(10)
        print('processor reset')

    def getDevEcho(self):
        '''Returns all possible entries for Echo setting of the RS-232 interface'''
        self.ser.write('GetDevInfo,Interface,0,Echo\n'.encode('utf-8'))
        devEcho = self.ser.readline()
        return devEcho

    def getDevBaud(self):
        '''Returns all possible baud rates of the RS-232 interface'''
        self.ser.write('GetDevInfo,Interface,0,BaudRate\n'.encode('utf-8'))
        possibleBaud = self.ser.readline()
        return devBaud

    def getDevInterface(self):
        '''Returns all possible interfaces'''
        self.ser.write('GetDevInfo,Interface,0,Name\n'.encode('utf-8'))
        devInterface = self.ser.readline()
        return devInterface

    def getBaud(self):
        '''Returns current baud rate of the RS-232 interface'''
        self.ser.write('Get,Interface,0,BaudRate\n'.encode('utf-8'))
        baudrate = self.ser.readline()
        return baudrate

    def getEcho(self):
        '''Returns current Echo setting for RS-232 interface'''
        self.ser.write('Get,Interface,0,Echo\n'.encode('utf-8'))
        echo = self.ser.readline()
        return echo

    def getInterface(self):
        '''Returns name of current interface'''
        self.ser.write('Get,Interface,0,Name\n'.encode('utf-8'))
        interfaceName = self.ser.readline()
        return interfaceName

    def setEcho(self, echo='Off'):
        '''Set the echo fuction On/Off. NOTE: turning echo 'On' can cause problems communicating with polytec.'''
        echo += '\n'
        self.ser.write(('Set,Interface,0,Echo,'+echo).encode('utf-8'))
        self.ser.write('Get,Interface,0,Echo\n'.encode('utf-8'))
        check = self.ser.readline()
        if check == echo:
            print('echo turned: ', check)
        else:
            print('ERROR: unable to change echo.')
            exit()

    def setBaud(self, baud=115200): #check baud rate??
        '''Set the baud rate for the RS-232 interface.  NOTE: this does NOT change the baudrate of the serial port.  If baudrate of interface is changed, may cause communication issues with serial port.'''
        baud = str(baud) + '\n'
        self.ser.write(('Set,Interface,0,BaudRate,'+baud).encode('utf-8'))
        self.ser.write('Get,Interface,0,BaudRate\n'.encode('utf-8'))
        check = self.ser.readline()
        if check == baud:
            print('baud rate changed to: ', check)
        else:
            print('ERROR: unable to change baud rate.')
            exit()

    def getDevName(self):
        '''Returns the name of the polytec sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,Name\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevVersion(self):
        '''Returns the firmware version of the sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,Version\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevFocus(self):
        '''Returns the focus range from minimum to maximum'''
        self.ser.write('GetDevInfo,SensorHead,0,Focus\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevManualFocus(self):
        '''Returns the possible states of the manual focus on the sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,ManualFocus\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevRemoteFocus(self):
        '''Returns possible states of the remote focus on the sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,RemoteFocus\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevAutoFocus(self):
        '''Returns possible states of the automatic focusing on the sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,AutoFocus\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevAutoFocusResult(self):
        '''Returns possible results of the automatic focusing on the sensor head'''
        self.ser.write('GetDevInfo,SensorHead,0,AutoFocusResult\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevAutoFocusArea(self):
        '''Returns the possibilities to set the automatic focus range'''
        self.ser.write('GetDevInfo,SensorHead,0,AutoFocusArea\n'.encode('utf-8'))
        return self.ser.readline()

    def getDevAutoFocusSpan(self):
        '''Returns the possibilities to set the range, which is around the automatic focus range (getAutoFocusArea)'''
        self.ser.write('GetDevInfo,SensorHead,0,AutoFocusSpan\n'.encode('utf-8'))
        return self.ser.readline()

    def getName(self):
        '''Returns the name of the sensor head'''
        self.ser.write('Get,SensorHead,0,Name\n'.encode('utf-8'))
        return self.ser.readline()

    def getVersion(self):
        '''Returns the firmware version of the sensor head'''
        self.ser.write('Get,SensorHead,0,Version\n'.encode('utf-8'))
        return self.ser.readline()

    def getFocus(self):
        '''Returns the actual focus position of the sensor head. First, the status of the controller is updated.'''
        mininum = 0
        maximum = 3300
        self.ser.write('Set,SensorHead,0,StatusUpdate\n'.encode('utf-8'))
        #setStatusUpdate(ser) #TESTTHIS!!
        self.ser.write('Get,SensorHead,0,Focus\n'.encode('utf-8'))
        return self.ser.readline()

    def getManualFocus(self):
        '''Returns the lock status of the manual focus on the sensor head'''
        self.ser.write('Get,SensorHead,0,ManualFocus\n'.encode('utf-8'))
        return self.ser.readline()

    def getRemoteFocus(self):
        '''Returns the status of the remote focus on the sensor head'''
        self.ser.write('Get,SensorHead,0,RemoteFocus\n'.encode('utf-8'))
        return self.ser.readline()

    def getAutoFocusResult(self):
        '''Returns the status of the auto focus on the sensor head'''
        self.ser.write('Get,SensorHead,0,AutoFocusResult\n'.encode('utf-8'))
        return self.ser.readline()

    def getAutoFocusArea(self):
        '''Returns the actual focus position'''
        self.ser.write('Get,SensorHead,0,AutoFocusArea\n'.encode('utf-8'))
        return self.ser.readline()

    def getAutoFocusSpan(self):
        '''Span of autofocus is returned whether the autofocus range is limited or not'''
        self.ser.write('Get,SensorHead,0,AutoFocusSpan\n'.encode('utf-8'))
        return self.ser.readline()

    def setStatusUpdate(self):
        '''Set status of the sensor head'''
        self.ser.write('Set,SensorHead,0,StatusUpdate,1\n'.encode('utf-8'))
        return self.ser.readline()

    def setFocusRange(self, focusRange):#TEST THIS
        '''Set focus range of the sensor head '''
        focusRange = str(focusRange) + '\n'
        self.ser.write(('Set,SensorHead,0,Focus'+focusRange).encode('utf-8'))
        check = getDevFocus()
        if check == focusRange:
            pass
        else:
            print('ERROR: Unable to change focus range')
            exit()
        return self.ser.readline()

    def setManualFocus(self, lock):
        '''Set the status of the manual focus on the sensor head, e.g. 'Unlocked' '''
        lock += '\n'
        self.ser.write(('Set,SensorHead,0,ManualFocus'+lock).encode('utf-8'))
        check = getManualFocus()
        if check == lock:
            pass
        else:
            print('ERROR: Unable to change status of manual focus')
            exit()

    def setRemoteFocus(self, remoteFocus):
        '''Sets the status of the remote focus on the sensor head'''
        remoteFocus += '\n'
        self.ser.write(('Set,SensorHead,0,RemoteFocus'+remoteFocus).encode('utf-8'))
        check = getRemoteFocus()
        if check == remoteFocus:
            pass
        else:
            print('ERROR: unable to set the remote focus of the sensor head')
            exit()

    def setAutoFocusArea(self, focusArea):
        '''Sets the area for the autofocus'''
        focusArea = str(focusArea) + '\n'
        self.ser.write(('Set,SensorHead,AutoFocusArea'+focusArea).encode('utf-8'))
        check = getAutoFocusArea()
        if check == focusArea:
            pass
        else:
            print('ERROR: Unable to set autofocus area')
            exit()

    def autofocusVibrometer(self, span='Full'):
        '''Autofocuses the vibrometer depending on chosen span (Full, Medium, Small)'''
        print('autofocusing vibrometer...')
        self.ser.write(('Set,SensorHead,0,AutoFocusSpan,'+span+'\n').encode('utf-8'))
        self.ser.write('Set,SensorHead,0,AutoFocus,Search\n'.encode('utf-8'))
        time.sleep(1)
        self.ser.write('Get,SensorHead,0,AutoFocusResult\n'.encode('utf-8'))
        focusAnswer = self.ser.readline()
        i = 0
        while focusAnswer != 'Found\n':
            self.ser.write('Get,SensorHead,0,AutoFocusResult\n'.encode('utf-8'))
            focusAnswer = self.ser.readline()
            time.sleep(1)
            if i > 30:
                break
            i += 1
        print('autofocus', focusAnswer)

    def getDevName(self, decoder='DD-300'):
        '''Returns either the name of the displacement decoder or "not Installed" if the decoder is not installed'''
        if decoder == 'DD-300':
            self.ser.write('GetDevInfo,DisplDec,0,Name\n'.encode('utf-8'))
            names = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('GetDevInfo,DisplDec,1,Name\n'.encode('utf-8'))
            names = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('GetDevInfo,VeloDec,1,Name\n'.encode('utf-8'))
            names = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('GetDevInfo,VeloDec,0,Name\n'.encode('utf-8'))
            names = self.ser.readline()
        return names

    def getDevRange(self, decoder='DD-300'):
        ''' Returns all possible measurement ranges for the decoder with physical units. "Not Available" returned if decoder not installed'''
        if decoder == 'DD-300':
            self.ser.write('GetDevInfo,DisplDec,0,Range\n'.encode('utf-8'))
            ranges = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('GetDevInfo,DisplDec,1,Range\n'.encode('utf-8'))
            ranges = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('GetDevInfo,VeloDec,1,Range\n'.encode('utf-8'))
            ranges = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('GetDevInfo,VeloDec,0,Range\n'.encode('utf-8'))
            ranges = self.ser.readline()
        return names

    def getDevResolution(self, decoder='DD-300'):
        '''Returns all possible resolution with physical units for the selected decoder, or "Not Available returned if decoder is not installed.'''
        if decoder == 'DD-300':
            self.ser.write('GetDevInfo,DisplDec,0,Resolution\n'.encode('utf-8'))
            resolution = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('GetDevInfo,DisplDec,1,Resolution\n'.encode('utf-8'))
            resolution = self.ser.readline()
        elif decoder == 'VD-09':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        elif decoder == 'VD-08':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        return resolution

    def getDevMaxFreq(self, decoder='DD-300'):
        '''Returns all possible maximum frequencies with physical units for the selected decoder, or "Not Available" if decoder  is not installed'''
        if decoder == 'DD-300':
            self.ser.write('GetDevInfo,DisplDec,0,MaxFreq\n'.encode('utf-8'))
            maxFreq = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('GetDevInfo,DisplDec,1,MaxFreq\n'.encode('utf-8'))
            maxFreq = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('GetDevInfo,VeloDec,1,MaxFreq\n'.encode('utf-8'))
            maxFreq = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('GetDevInfo,VeloDec,0,MaxFreq\n'.encode('utf-8'))
            maxFreq = self.ser.readline()
        return maxFreq

    def getDevDelay(self, decoder='DD-300'):
        '''Returns all measurement ranges with physical units for the selected decoder, or "Not Available" if decoder is not installed'''
        if decoder == 'DD-300':
            self.ser.write('GetDevInfo,DisplDec,0,SignalDelay\n'.encode('utf-8'))
            signalDelay = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('GetDevInfo,DisplDec,1,SignalDelay\n'.encode('utf-8'))
            signalDelay = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('GetDevInfo,VeloDec,1,SignalDelay\n'.encode('utf-8'))
            signalDelay = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('GetDevInfo,VeloDec,0,SignalDelay\n'.encode('utf-8'))
            signalDelay = self.ser.readline()
        return signalDelay

    def getName(self, decoder='DD-300'):
        '''Returns the name of the decoder, e.g. DD-300'''
        if decoder == 'DD-300':
            self.ser.write('Get,DisplDec,0,Name\n'.encode('utf-8'))
            name = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('Get,DisplDec,1,Name\n'.encode('utf-8'))
            name = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('Get,VeloDec,1,Name\n'.encode('utf-8'))
            name = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('Get,VeloDec,0,Name\n'.encode('utf-8'))
            name = self.ser.readline()
        return name

    def getRange(self, decoder='DD-300'):
        '''Returns current measurement range with physical units, e.g. 125mm/s/V'''
        if decoder == 'DD-300':
            self.ser.write('Get,DisplDec,0,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('Get,DisplDec,1,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('Get,VeloDec,1,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('Get,VeloDec,0,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
        return therange

    def getResolution(self, decoder='DD-300'):
        '''Returns resolution with unit of selected decoder, e.g. 5120 nm.  Only valid for displacement decoers'''
        if decoder == 'DD-300':
            self.ser.write('Get,DisplDec,0,Resolution\n'.encode('utf-8'))
            resolution = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('Get,DisplDec,1,Resolution\n'.encode('utf-8'))
            resolution = self.ser.readline()
        elif decoder == 'VD-09':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        elif decoder == 'VD-08':
            print('ERROR: resolution only available for displacement decoders')
            exit()
        return resolution

    def getMaxFreq(self, decoder='DD-300'):
        '''Returns maximum frequency of the selected decoder with unit for current range of decoder, e.g. 20MHz.'''
        if decoder == 'DD-300':
            self.ser.write('Get,DisplDec,0,MaxFreq\n'.encode('utf-8'))
            frequency = self.ser.readline()
        elif decoder == 'DD-900':
            self.ser.write('Get,DisplDec,1,MaxFreq\n'.encode('utf-8'))
            frequency = self.ser.readline()
        elif decoder == 'VD-09':
            self.ser.write('Get,VeloDec,1,MaxFreq\n'.encode('utf-8'))
            frequency = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('Get,VeloDec,0,MaxFreq\n'.encode('utf-8'))
            frequency = self.ser.readline()
        return frequency

    def getDelay(self, decoder='DD-300'):
        '''Returns (typical) signal transit time delay for the selected decoder with units, e.g. 8.16 us'''
        if decoder == 'DD-300':
            delay = '0 us'
        elif decoder == 'DD-900':
            delay = '0 us'
        elif decoder == 'VD-09':
            self.ser.write('Get,VeloDec,1,SignalDelay\n'.encode('utf-8'))
            delay = self.ser.readline()
        elif decoder == 'VD-08':
            self.ser.write('Get,VeloDec,0,SignalDelay\n'.encode('utf-8'))
            delay = self.ser.readline()
        return delay

    def setRange(self, decoder='DD-300', drange='5mm/s/V'):
        '''setRange'''
        if decoder == 'DD-300':
            # set VD-09 range for DD-300
            self.ser.write(('Set,VeloDec,1,Range,' + drange + '\n').encode('utf-8'))
            self.ser.write('Get,VeloDec,1,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
            self.ser.write('Get,DisplDec,0,Name\n'.encode('utf-8'))
            thename = self.ser.readline()
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'DD-900':
            self.ser.write(('Set,VeloDec,1,Range,' + drange + '\n').encode('utf-8'))
            self.ser.write('Get,VeloDec,1,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
            self.ser.write('Get,DisplDec,1,Name\n'.encode('utf-8'))
            thename = self.ser.readline()
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-09':
            self.ser.write(('Set,VeloDec,1,Range,' + drange + '\n').encode('utf-8'))
            self.ser.write('Get,VeloDec,1,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
            self.ser.write('Get,VeloDec,1,Name\n'.encode('utf-8'))
            thename = self.ser.readline()
            print('decoder: ' + thename)
            print('range of VD-09 set to: ' + therange)

        elif decoder == 'VD-08':
            self.ser.write(('Set,VeloDec,0,Range,' + drange + '\n').encode('utf-8'))
            self.ser.write('Get,VeloDec,0,Range\n'.encode('utf-8'))
            therange = self.ser.readline()
            self.ser.write('Get,VeloDec,0,Name\n'.encode('utf-8'))
            thename = self.ser.readline()
            print('decoder: ' + thename)
            print('range of VD-08 set to: ' + therange)

