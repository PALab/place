from __future__ import print_function
import serial
import time
'''
Driver module for Newport's Spectra-Physics Quanta-Ray INDI, PRO, and LAB Series Nd:YAG lasers. 

**NOTE: the watchdog parameter is important!  The laser will turn off if it does not receive a command within the watchdog time period.  Therefore, it is advised to use a command like QRstatus().getStatus() at regular intervals to query the status of the laser during operation. 

The module is organized in four classes:
-QuantaRay()
    Basic functions for the laser system.  Set up serial connection, turn on/off, and set/read lamp settings.
-QSW()
    Set and read QSW parameters
-QRcomm()
    Communication functions for laser: echo, baudrate, watchdog
-QRread()
    Functions to query what the laser is actually doing.
-QRstatus()
    Returns status information about the laser.

Examples:
to open a connection:
from place.automate.quanta_ray.QRay_driver import QuantaRay
QuantaRay().openConnection('/dev/ttyUSB0')

to turn on laser:
from place.automate.quanta_ray.QRay_driver import QuantaRay
QuantaRay().on()

to set QSW to rep rate:
from place.automate.quanta_ray.QRay_driver import QSW
QSW().set(cmd='REP')

to set watchdog time:
from place.automate.quanta_ray.QRay_driver import QRcomm
QRcomm().setWatchdog(time=60) #set watchdog to 60 seconds

to query statu of laser:
from place.automate.quanta_ray.QRay_driver import QRstatus
error = QRstatus().getStatus()
print error #prints error status

@author: Jami L Johnson
September 5, 2014
'''

class QuantaRay:

    def __init__(self, portINDI='/dev/ttyUSB0', baudINDI=9600):
        '''Define serial port for INDI'''
        self.indi = serial.Serial( 
            port = portINDI,
            baudrate = baudINDI,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_TWO,
            bytesize = serial.EIGHTBITS
            )

    def openConnection(self):
        ''' Open serial connection to INDI'''
        self.indi.close()
        self.indi.open()
        indiOpen = self.indi.isOpen()
        if indiOpen == True:
            print('connected to: ', QuantaRay().getID())
        else:
            print('ERROR: unable to connect to INDI')
            exit()

    def closeConnection(self):
        '''Close connection to INDI'''
        self.indi.close()
        print('connection to INDI closed')
    
    def getID(self):
        self.indi.write('*IDN?\r')
        ID = self.indi.readline()
        return ID

    def help(self):
        '''Prints serial command options (operational commands)'''
        self.indi.write('HELP\r')
        for i in range(1,6):
            print(self.indi.readline())

    def on(self):
        '''Turns Quanta-Ray INDI on'''
        self.indi.write('ON\r')
        print('INDI turned on')

    def off(self):
        '''Turns Quanta-Ray INDI off'''
        self.indi.write('OFF\r')
        print('INDI turned off')
        
    def setLamp(self,lampSet='FIX',lampPulse=''):
        '''
        Select lamp trigger source
        lampSet:
        FIX = set lamp trigger to Fixed
        EXT = set lamp trigger to External Source
        VAR = set lamp trigger to Variable
        INH = inhibit lamp trigger

        lampPulse = set rate of lamp (pulses/second) 
        '''
        if lampPulse != '':
           self.indi.write('LAMP '+ str(lampSet) + ' ' + str(lampPulse) + '\r')
        else:
            self.indi.write('LAMP '+ str(lampSet) + '\r')

    def getLamp(self):
        ''' Returns the lamp Variable Rate trigger setting '''
        self.indi.write('LAMP VAR?\r')
        return self.indi.readline()

    def set(self, cmd='NORM'):
        '''
        Set mode, type, or timing of Q-switch
        cmd:
        LONG = long pulse mode
        EXT = external mode
        NORM = normal mode
        SING = single shot
        FIR = fire Q-switch once
        REP = repetitive shots
        '''
        self.indi.write('QSW ' + str(cmd) + '\r')

    def get(self):
        '''
        Queries and returns the Q-switch settings.
        '''
        self.indi.write('QSW?\r')
        return self.indi.readline()
    
    def setAdv(self, delay=''):
        if delay != '':
            self.indi.write('ADV ' + str(delay) + '\r')
        else:
            print('No advanced sync delay set, no command sent to laser')

    def getAdv(self):
        '''Queries and returns the Q-switch Advanced Sync settings'''
        self.indi.write('QSW ADV? \r')
        return self.indi.readline()

    def setDelay(self,delay=''):
        '''Sets delay for Q-switch delay'''
        if delay != '':
            self.indi.write('QSW DEL ' + str(delay) + '\r')
        else:
            print('No delay set, no command sent to laser')

    def getDelay(self):
        '''Queries and returns the Q-switch delay setting'''  
        self.indi.write('QSW DEL? \r')
        return self.indi.readline()
    
    def setEcho(self,mode=0):
        '''
        Set echo mode of INDI.
        mode:
        0 = show prompts
        1 = laser echoes characters as received
        2 = shows error messages
        3 = output line feed for every command (even those that don't normally generate a response)
        4 = terminate responses with <cr><lf>, rather than just <lf>
        5 = use XON/XOFF handshaking for data sent to laser (not for data sent from the laser)
    '''
        self.indi.write('ECH ' + str(mode) + '\r')
        print('Echo mode set to: ', str(mode))

    def setWatchdog(self, time=10):
        '''
        Set range of watchdog.  If the laser does not receive communication from the control computer within the specifiedc time, it turns off.  If disabled, the default time is zero.  time must be between 0 and 110 seconds.
        '''
        if time < 0 or time > 110:
            print('Invalid watchdog time.  Choose value between 0 and 110 seconds.')
            exit()
        else:
            self.indi.write('WATC ' + str(time) + '\r')
            print('Watchdog set to ', str(time), ' seconds')

    def setBaud(self, baudINDI=9600):
        '''
        Sets baudrate of laser.  At power-up, baudrate is always 9600.
        '''
        self.indi.write('BAUD ' + str(baudINDI) + '\r')
        print('Baudrate of INDI set to ', str(baudINDI))

    def getAmpSetting(self):
        '''Queries amplifier PFN command setting in percent'''
        self.indi.write('READ:APFN?\r')
        APFN = self.indi.readline()  
        return APFN

    def getAmpPower(self):
        '''Queries amplifier PFN monitor in percent (what PFN power supply is actually doing)'''
        self.indi.write('READ:AMON?\r')
        AMON = self.indi.readline()
        return AMON

    def getOscSetting(self):
        '''Queries oscillator PFN command setting in percent'''
        self.indi.write('READ:OPFN?\r')
        OPFN = self.indi.readline()
        return OPFN

    def getOscPower(self):
        '''Queries oscillator PFN monitor in percent (what PFN power supply is actually doing)'''
        self.indi.write('READ:OMON?\r')
        OMON = self.indi.readline()
        return OMON

    def getAdv(self):
        '''Queries and returns the current Q-Switch Advanced Sync setting'''
        self.indi.write('READ:QSWADV?\r')
        QSW = self.indi.readline()
        return QSW

    def getShots(self):
        '''Queries and returns the number of shots'''
        self.indi.write('SHOT?\r')
        print(self.indi.readline())

    def getTrigRate(self):
        '''Queries and returns the lamp trigger rate (unless lamp trigger source is external'''
        self.indi.write('READ:VAR?\r')
        tRate = self.indi.readline()
        print(tRate)
        return tRate
    
    def setOscPower(self, percent=0):
        '''set the Oscillator PFN voltage as a percentage of factory full scale'''
        self.indi.write('OPFN ' + str(percent) + '\r')

    def getStatus(self):
        '''
        Returns the laser status.  
        Result is a list with entries of the form: [bit, error], where "bit" is the bit of the status byte, and "error" is a text description of the error.
        '''

        self.indi.write('*STB?\r')

        STB = bin(int(self.indi.readline()))
        STB = STB[2:] # remove 0b at beginning
        #print 'STB: ', STB # prints binary status byte value
    
        errorList = list() 
       
        if STB[len(STB)-1] == '1': 
            bit = '0'
            error = 'Laser emission can occur'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-2] == '1': 
            bit = '1'
            error = 'Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-3] == '1': 
            bit = '2'
            error = 'Data is in the error log.  \n (use QRstatus().getHist() for details on the error.)'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-4] == '1': 
            bit = '3'
            error = 'Check QRstatus().getQuest() for error'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-5] == '1': 
            bit = '4'
            error = 'Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-6] == '1': #5 **********
            bit = '5'
            error = 'Check *ESR bits for error.'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-7] == '1': 
            bit = '6'
            error = 'Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-8] == '1': #7 ****
            bit = '7'
            error = 'Check STR:OPER bits'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-9] == '1': 
            bit = '8'
            error = 'Main contactor is energized'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-10] == '1': 
            bit = '9'
            error = 'Oscillator simmer is on'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-11] == '1': 
            bit = '10'
            error = 'Amplifier simmer is on'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-12] == '1': 
            bit = '11'
            error = 'Oscillator PFN is at target'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-13] == '1': 
            bit = '12'
            error = 'The laser has recently fired'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-14] == '1': 
            bit = '13'
            error = '15 Vdc power supply failure'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-15] == '1': 
            bit = '14'
            error = 'Laser cover interlock open'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-16] == '1': 
            bit = '15'
            error = 'Interlock open: CDRH plug, power supply cover, laser head cover, laser head temperature, water pressure, or water flow'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-17] == '1': 
            bit = '16'
            error = 'Remote panel disconnected'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-18] == '1': 
            bit = '17'
            error = 'Internal 208 Vac failure'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-19] == '1': 
            bit = '18'
            error = 'CDRH enable failure'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-20] == '1': 
            bit = '19'
            error = 'Laser ID fault'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-21] == '1': 
            bit = '20'
            error = 'Low water fault'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-22] == '1': 
            bit = '21'
            error = 'Interlock fault'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-23] == '1': 
            bit = '22'
            error = 'Remote panel connected'
            stat = [bit,error]
            errorList.append(stat)
        if STB[len(STB)-24] == '1': 
            bit = '23'
            error = 'Remote panel indicates that the computer is in control.'
            stat = [bit,error]
            errorList.append(stat)
        if len(STB) > 24: 
            if STB[len(STB)-25] == '1': 
                bit = '24'
                error = 'Main contactor should be on.'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-26] == '1': 
                bit = '25'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-27] == '1': 
                bit = '26'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-28] == '1': 
                bit = '27'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-29] == '1': 
                bit = '28'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-30] == '1': 
                bit = '29'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-31] == '1': 
                bit = '30'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
            if STB[len(STB)-31] == '1': 
                bit = '32'
                error = 'Reserved error'
                stat = [bit,error]
                errorList.append(stat)
        return errorList

    def getQuest(self):
        '''
        Returns questionable condition register.
        Result is a list with entries of the form: [bit, error], where "bit" is the bit of the status byte, and "error" is a text description of the error. 
        '''
        self.indi.write('STAT:QUES?\r')

        QB = bin(int(self.indi.readline()))
        QB = QB[3:]
   
        errorList = list()
        #print 'QB: ', QB # prints binary STAT:QUES? value
        
        if QB[len(QB)-1] == '1': 
            bit = '0'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-2] == '1': 
            bit = '1'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-3] == '1':
            bit = '2'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-4] == '1':
            bit = '3'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-5] == '1':
            bit = '4'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-6] == '1':
            bit = '5'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-7] == '1':
            bit = '6'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-8] == '1':
            bit = '7'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-9] == '1':
            bit = '8'
            error = '-Reserved error'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-10] == '1':
            bit = '9'
            error = '-Oscillator HV failure'
            stat = [bit,error]
            errorList.append(stat)
            QuantaRay().off()
            exit()
        if QB[len(QB)-11] == '1':
            bit = '10'
            error = '-Amplifier HV failure'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-12] == '1':
            bit = '11'
            error = '-External trigger rate out of range.'
            stat = [bit,error]
            errorList.append(stat)
        if QB[len(QB)-13] == '1':
            bit = '12'
            error = '-De-ionized water low'
            stat = [bit,error]
            errorList.append(stat)
        if len(QB) > 15:
        # bits 13-15 undefined
            if QB[len(QB)-17] == '1':
                bit = '16'
                error = '-OSC HVPS # 1 EndOfCharge'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-18] == '1':
                bit = '17'
                error = '-OverLoad'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-19] == '1':
                bit = '18'
                error = '-OverTemp'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-20] == '1':
                bit = '19'
                error = '-OverVolt'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-21] == '1':
                bit = '20'
                error = '-OSC HVPS #2 EndOfCharge'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-22] == '1':
                bit = '21'
                error = '-OverLoad'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-23] == '1':
                bit = '22'
                error = '-OverTemp'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-24] == '1':
                bit = '23'
                error = '-OverVolt'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-25] == '1':
                bit = '24'
                error = '-AMP HVPS # 1 EndOfCharge'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-26] == '1':
                bit = '25'
                error = '-OverLoad'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-27] == '1':
                bit = '26'
                error = '-OverTemp'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-28] == '1':
                bit = '27'
                error = '-OverVolt'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-29] == '1':
                bit = '28'
                error = '-AMP HVPS # 2 EndOfCharge'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-30] == '1':
                bit = '29'
                error = '-OverLoad'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-31] == '1':
                bit = '30'
                error = '-OverTemp'
                stat = [bit,error]
                errorList.append(stat)
            if QB[len(QB)-32] == '1':
                bit = '31'
                error = '-OverVolt'
                stat = [bit,error]
                errorList.append(stat)
        return errorList

    def reset(self):
        ''' Resets the laser head PC board'''
        self.indi.write('*RST?\r')
        print('Laser PC board reset')
        
    def getHist(self):
        '''
        Returns up to 16 status/error codes from the system history buffer.  
        Use if the laser has shut off or the system is behaving erratically. 
        The first element is the most recent.
        Example output:
        1 827 # 1 error has occured, current time is 827 sec
        301 801 # Error code 301 occured at 810 seconds
        0 0 # End of history buffer
        '''

        self.indi.write('READ:HIST?\r')

        reply = '1'
        replyList = list()
        while reply[0] != '0': #end of history buffer
            reply = self.indi.readline().rstrip()
            replyList.append(reply)

        return replyList
    
