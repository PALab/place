import serial
from time import sleep
from string import atoi
from struct import pack
import matplotlib.pyplot as plt

'''
Driver module for Stanford Research Systems DS345 Function Generator.  A few examples are shown below.  More detailed examples can be found in the test_DS345.py script.
 
Examples:
to open a connection:
from place.automate.SRS.DS345_driver import DS345
DS345().openConnection(fgenPort='/dev/ttyS0')

Set output waveform parameters:
from place.automate.SRS.DS345_driver import Generate
Generate().functOutput(amp=1,ampUnits='VP',freq=10000,sampleFreq=1,funcType='square',invert='on',offset=2,phase=10,aecl='n',attl='n')

from place.automate.SRS.DS345_driver import Modulate
Modulate().enable() # enables waveform modulation
Modulate().setStartFreq(startFreq=5) # set starting frequency for a sweep
print Modulate().getStartFreq() # print starting frequency

from place.automate.SRS.DS345_driver import Test
Test().selfTest() # run basic self tests

from place.automate.SRS.DS345_driver import Calibrate
Calibrate().routines() # run factory calibration routine
'''

class DS345:
    ''' Basic setup functions for the SRS DS345 function generator'''

    def __init__(self,fgenPort='/dev/ttyS0'):
        '''Define settings for RS-232 serial port'''
        self.fgen = serial.Serial(
            port=fgenPort,
            timeout=1, 
            baudrate=9600,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE
            )
        
    def openConnection(self,fgenPort='/dev/ttyS0'): 
        '''
        Open serial port for DS345 function generator
        '''
        self.fgen.close()
        self.fgen.open()

        funGenOpen = self.fgen.isOpen()
        if funGenOpen == True:
            ID = DS345().getID()
            print 'connected to DS345: ', ID
        else:
            print 'ERROR: unable to connect to DS345 function generator'
            exit()

    def closeConnection(self):
        self.fgen.close()
        print 'Connection to DS345 is closed'
 
    def getID(self):
        '''
        Prints and returns DS345's divice configuration.
        format: StanfordResearchSystems,DS345,serial number,version number
        '''
        self.fgen.write('*IDN? \n')
        sleep(1)
        IDN = self.fgen.readline().rstrip()
        return IDN
    
    def getSettings(self, setNum=0):
        '''
        Recalls stored setting number (0 to 9). Results are printed and returned by the function.
        '''
        self.fgen.write('*RCL ' + str(setNum) + ' \n')
        sleep(1)
        RCL = self.fgen.readline().rstrip()
        print RCL
        return RCL

    def setDefault(self):
        '''
        Resets DS345 to default configurations.
        '''
        self.fgen.write('*RST \n')
        sleep(1)
        print 'Default settings restored'

    def saveSettings(self, setNum=0):
        '''
        Sets current instrument settings to the DS345 (0 through 9).
        setNum = identifying number for current settings
        '''
        self.fgen.write('*SAV ' + str(setNum) + ' \n')
        sleep(1)
        print 'Current settings saved as setting number: ', str(setNum)
        
        
class Generate(DS345):
    ''' Set parameters for output waveform of SRS DS345'''

    def functOutput(self,amp=10,ampUnits='VP',freq=1000,sampleFreq=1,funcType='sine',invert='off',offset=0,phase=0,aecl='n',attl='n'):
        '''
        Set parameters of output waveform

        Input paramters:
        amp = output amplitude
        ampUnits = amplitude units: 'VP' (Vpp),'VR' (Vrms), 'DB' (dBm)
        **NOTE: for arbitary waveforms, the amplitude units must be set to 'VP'
        freq = output frequency (Hz).  1 microHz resolution
        sampleFreq = sampling frequency of output
        funcType = output function type: 'sine','square','triangle','ramp','noise','arb'
        invert = turn output inversion on: 'on' or 'off'
        offset = sets DC offset (V)
        phase = set waveform phase (degrees)
        aecl = to set the output of th ECL levels to 1 Vpp with a -1.3 V offset (-1.8V to -0.8V). 'y' or 'n'
        attl = set the TTL output levels of 5 Vpp with a 2.5 V offset (0V to 5V). 'y' or 'n'
        '''
        # set amplitude
        self.fgen.write('AMPL ' + str(amp) + str(ampUnits) + ' \n')
        sleep(1)
        self.fgen.write('AMPL?\n')
        print 'Amplitude = ', self.fgen.readline().rstrip()


        # set output frequency
        self.fgen.write('freq ' + str(freq) + ' \n')
        sleep(1)
        self.fgen.write('freq? \n')
        freqCheck = self.fgen.readline().rstrip()
        print 'Frequency = ', freqCheck, 'Hz'

        # set sampling frequency
        self.fgen.write('fsmp ' + str(sampleFreq) + ' \n')
        sleep(1)
        self.fgen.write('fsmp? \n')
        sfreqCheck = self.fgen.readline().rstrip()
        print 'Sampling frequency = ', sfreqCheck, 'Hz'

        # set function type
        if funcType == 'sine':
            self.fgen.write('func 0 \n')
        elif funcType== 'square':
            self.fgen.write('func 1 \n')
        elif funcType== 'triangle':
            self.fgen.write('func 2 \n')
        elif funcType== 'ramp':
            self.fgen.write('func 3 \n')
        elif funcType== 'noise':
            self.fgen.write('func 4 \n')
        elif funcType== 'arb':
            self.fgen.write('func 5 \n')
        else: 
            print 'ERROR: Invalid function type.'
            exit()

        sleep(1)

        # check function type
        self.fgen.write('func? \n')
        funcCheck = atoi(self.fgen.readline())          
        if funcCheck == 0:
            print 'Output waveform = sine'
        elif funcCheck == 1:
            print 'Output waveform = square'
        elif funcCheck == 2:
            print 'Output waveform = triangle'
        elif funcCheck == 3:
            print 'Output waveform = ramp'
        elif funcCheck == 4:
            print 'Output waveform = noise'
        elif funcCheck == 5:
            print 'Output waveform = arbitrary'
        else: 
            print 'ERROR: Unable to read waveform type.'
            exit()

        if aecl == 'y':
            self.fgen.write('aecl \n')
            print 'ECL levels to 1Vpp with a -1.3V offset.'
        if attl == 'y':
            self.fgen.write('attl \n')
            print 'TTL levels of 5Vpp with a 2.5V offset.'

        # set output offset
        self.fgen.write('offs ' + str(offset) + ' \n')
        sleep(1)
        self.fgen.write('offs? \n') # check offset
        oCheck = self.fgen.readline().rstrip() 
        print 'Offset = ', oCheck,'V'

        # set phase of waveform
        if phase == 0:
            self.fgen.write('pclr \n')
        else:
            self.fgen.write('phse ' + str(phase) + ' \n')
            
        sleep(1)
        self.fgen.write('phse? \n')
        phaseCheck = self.fgen.readline().rstrip() # check phase
        print 'Waveform phase = ', phaseCheck, ' degrees'

        # turn output inversion on/off
        if invert == 'on':
            self.fgen.write('invt 1 \n')
        elif invert == 'off':
            self.fgen.write('invt 0 \n')

        sleep(1)

        # check and print inversion status
        self.fgen.write('invt? \n')
        iCheck = atoi(self.fgen.readline()) # check inversion status
        if iCheck == 1:
            print 'Waveform inverted'

class Modulate(DS345):
    '''Set modulation parameters'''

    def enable(self):
        '''Enable modulation'''

        self.fgen.write('mena 1 \n') # enables modulations
        sleep(1)
        self.fgen.write('mena? \n')
        mena = self.fgen.readline().rstrip()
        if mena == '1':
            print 'Modulation enabled'

    def setBurstCount(self, burstCount=1):
        '''
        Set burst parameters
        burstCount = sets the burst count (1 to 30000)
        
        '''
        # set burstcount
        self.fgen.write('bcnt ' + str(burstCount) + ' \n')
        sleep(1)

    def getBurstCount(self):
        '''
        Returns current burst count
        '''
        self.fgen.write('bcnt? \n')
        burstCount = self.fgen.readline().rstrip()
        print 'Burst count = ', burstCount
        return burstCount

    def setAMDepth(self,depth=100):
        '''
        Set AM modulation depth (0 to 100%).  
        '''
        if depth < 0 or depth > 100:
            print 'ERROR: Modulation depth must be between 0 and 100%'
            exit()
        else:
            self.fgen.write('dpth ' + str(depth) + ' \n')
            sleep(1)
    
    def getAMDepth(self):
        '''
        Returns current AM modulation depth (%)
        '''
        self.fgen.write('dpth? \n')
        amDepth = self.fgen.readline().rstrip()
        print 'AM depth = ', amDepth
        return amDepth

    def setFMSpan(self,span=1):
        '''
        Set FM span (Hz). Frequency must be greater than zero or less than frequency allowed for selected function.  Waveform centered on the front panel frequency and will have a deviation of +/- span/2.
        '''
        self.fgen.write('fdev ' + str(span) + ' \n')
        sleep(1)
    
    def getFMSpan(self):
        '''
        Returns current FM Span (Hz)
        '''
        self.fgen.write('fdev? \n')
        fdev = self.fgen.readline().rstrip()
        print 'FM span set to ', fdev, ' Hz'
        return fdev

    def setModWaveform(self,modType='single'):
        '''
        Sets the modulation waveform.
        'single' (single sweep), 'ramp',  'triangle', 'sine', 'square', 'arb', 'none'
        **NOTE: 'arb' = arbitrary waveform, and may only be set for AM, FM and PM.  The waveform must be downloaded via the Arbitrary().loadModulationPattern() function.
        '''
        if modType == 'single':
            self.fgen.write('mdwf 0 \n')
        elif modType == 'ramp':
            self.fgen.write('mdwf 1 \n')
        elif modType == 'triangle':
            self.fgen.write('mdwf 2 \n')
        elif modType == 'sine':
            self.fgen.write('mdwf 3 \n')
        elif modType == 'square':
            self.fgen.write('mdwf 4 \n')
        elif modType == 'arb':
            self.fgen.write('mdwf 5 \n')
        elif modType == 'none':
            self.fgen.write('mdwf 6 \n')
        else:
            print 'ERROR: Invalid modulation waveform type'
            exit()
    
        sleep(1)

    def getModWaveform(self):
        '''
        Returns modulation waveform type
        '''
        self.fgen.write('mdwf? \n')
        modCheck = atoi(self.fgen.readline().rstrip())
        
        if modCheck == 0:
            wfrm = 'single'
            print 'Modulation waveform = single'
        elif modCheck == 1:
            wfrm = 'ramp'
            print 'Modulation waveform = ramp'
        elif modCheck == 2:
            wfrm = 'triangle'
            print 'Modulation waveform = triangle'
        elif modCheck == 3:
            wfrm = 'sine'
            print 'Modulation waveform = sine'
        elif modCheck == 4:
            wfrm = 'square'
            print 'Modulation waveform = square'
        elif modCheck == 5:
            wfrm = 'arbitrary'
            print 'Modulation waveform = arbitrary'
        elif modCheck == 6:
            wfrm = 'none'
            print 'Modulation waveform = none'
        return wfrm

    def setSweepExtreme(self):
        '''
        Sets the sweep markers to the extremes of the sweep span.  The marker start frequency is set to the sweep start frequency and the marker stop frequency is set to the sweep stop frequency.
        '''
        self.fgen.write('mksp \n')
        sleep(1)
        print 'Sweep markers set to extremes of span'

    def setSweepFreq(self,markerType='start',markerFreq=0):
        '''
        Sets the sweep marker freuqency. 
        markerType = choose frequency for the 'start', 'stop', or 'center' of the sweep, or set the frequency 'span'.
        markerFreq = frequency to set markerType to.
        '''

        if markerType == 'start':
            self.fgen.write('mrkf 0,' + str(markerFreq) + ' \n')
        elif markerType == 'stop':
            self.fgen.write('mrkf 1,' + str(markerFreq) + ' \n')
        elif markerType == 'center':
            self.fgen.write('mrkf 2,' + str(markerFreq) + ' \n')
        elif markerType == 'span':
            self.fgen.write('mrkf 3,' + str(markerFreq) + ' \n')
        else: 
            print 'ERROR: Invalid marker type.'
            exit()
        sleep(1)
        
    def getSweepFreq(self,markerType='start'):
        '''
        Returns the sweep marker frequency
        '''

        if markerType == 'start':
            self.fgen.write('mrkf? 0 \n')
            markFreqCheck = self.fgen.readline().rstrip()
            print 'Modulation ', markerType, ' frequency set to: ', markFreqCheck, ' Hz.'
     
        elif markerType == 'stop':
            self.fgen.write('mrkf? 1 \n')
            markFreqCheck = self.fgen.readline().rstrip()
            print 'Modulation ', markerType, ' frequency set to: ', markFreqCheck, ' Hz.'

        elif markerType == 'center':
            self.fgen.write('mrkf? 2 \n')
            markFreqCheck = self.fgen.readline().rstrip()
            print 'Modulation ', markerType, ' frequency set to: ', markFreqCheck, ' Hz.'

        elif markerType == 'span':
            self.fgen.write('mrkf? 3 \n')
            markFreqCheck = self.fgen.readline().rstrip()
            print 'Modulation ', markerType, ' frequency set to: ', markFreqCheck, ' Hz.'

        else: 
            print 'ERROR: Invalid marker type.'
            exit()
        return markFreqCheck
            
    def setModType(self,modType='Linear'):
        '''
        Sets modulation type:

        'linear', 'log', 'AM', 'FM', 'PM', 'burst'
        '''
        if modType == 'linear':
            self.fgen.write('mtyp 0 \n')
        elif modType == 'log':
            self.fgen.write('mtyp 1 \n')
        elif modType == 'AM':
            self.fgen.write('mtyp 2 \n')
        elif modType == 'FM':
            self.fgen.write('mtyp 3 \n')
        elif modType == 'PM':
            self.fgen.write('mtyp 4 \n')
        elif modType == 'burst':
            self.fgen.write('mtyp 5 \n')
        else:
            print 'ERROR: Invalid modulation type.'
            exit()

        sleep(1)
    
    def getModType(self):
        '''
        Returns modulation type
        '''
        self.fgen.write('mtyp? \n')
        mtype = self.fgen.readline().rstrip()
        mtypeCheck = mtype[0]
        if mtypeCheck == '0':
            modType = 'linear'
            print 'Modulation type = linear'
        elif mtypeCheck == '1':
            modType = 'log'
            print 'Modulation type = log'
        elif mtypeCheck == '2':
            modType = 'internal AM'
            print 'Modulation type = internal AM'
        elif mtypeCheck == '3':
            modType = 'FM'
            print 'Modulation type = FM'
        elif mtypeCheck == '4':
            modType = 'PM'
            print 'Modulation type = PM'
        elif mtypeCheck == '5':
            modType = 'burst'
            print 'Modulation type = burst'
        return modType

    def setPhaseMod(self,modPhase=0):
        '''
        Sets the span of the phase modulation.  Range from 0 to 7199.999 degrees. Phase shift ranges from -span/2 to span/2.
        
        modPhase = modulation phase (degrees)
        '''
        if modPhase < 0 or modPhase > 7199.999:
            print 'Phase out of range.  Choose a value between 0 and 7199.999 degrees.'
            exit()
        else:
            self.fgen.write('pdev '+ str(modPhase) + ' \n')
            sleep(1)

    def getPhaseMod(self):
        '''
        Queries and returns span of phase  modulation (degrees)
        '''
        self.fgen.write('pdev? \n')
        phaseMod = self.fgen.readline().rstrip()
        print 'Phase modulation set to: ', phaseMod, 'degrees'
        return phaseMod

    def setModRate(self,modRate=1):
        '''
        Sets the  modulation rate.  Rounded to 2 significant digits.  Ranges from 0.001 Hz to 10 kHz.

        modRate = modulation rate (Hz)
        '''
        if modRate < 0.001 or modRate > 10000:
            print 'Modulation rate out of range.  Choose a value between 0.001 and 10000 Hz.'
            exit()
        else:
            self.fgen.write('rate ' + str(modRate) + ' \n')
            sleep(1)

    def getModRate(self):
        '''
        Queries and returns modulation rate (Hz)
        '''
        self.fgen.write('rate? \n')
        modRate = self.fgen.readline().rstrip()
        print 'Modulation rate set to: ', modRate, 'Hz'
        return modRate

    def setSpanFreq(self,spanFreq=1):
        '''
        Sets the sweep span. Span must be greater than 0 and within range allowed by current function.  Sweeps from (center frequency - span/2) to (center frequency + span/2).  Negative span generates a downward sweep from max to min frequency.
       
        spanFreq = sweep span (Hz).  
        '''
        if spanFreq < 0:
            print 'ERROR: sweep span must be greater than 0.'
            exit()
        else:
            self.fgen.write('span '+ str(spanFreq) + ' \n')
            sleep(1)

    def getSpanFreq(self):
        '''
        Queries and returns frequency span of sweep (Hz).
        '''
        self.fgen.write('span? \n')
        span = self.fgen.readline().rstrip()
        print 'Frequency span of sweep set to: ', span, 'Hz'
        return span
        
    def setCenterFreq(self,centerFreq=5):
        '''
        Sets center frequency of the sweep. Must be greater than zero and less than greatest frequency allowed by the current function.
       
        centerFreq = center frequency of sweep (Hz)
        '''
        if centerFreq <= 0:
            print 'ERROR: Center frequency must be greater than 0.'
            exit()
        else:
            self.fgen.write('spcf ' + str(centerFreq) + ' \n')
            sleep(1)
            self.fgen.write('spcf? \n')
            print 'Center frequency of sweep set to: ', self.fgen.readline().rstrip()

    def setStopFreq(self,stopFreq=10):
        '''
        Sets stop frequency of sweep.  Frequency must be greater than zero and less than greatest frequency allowed by the current function.  If stop frequency is less than start frequency, a downward sweep from max to min frequency will be generated. 

        stopFreq = stop frequency of sweep (Hz)
        '''
        if stopFreq <= 0:
            print 'ERROR: Stop frequency must be greater than 0.'
            exit()
        else:
            self.fgen.write('spfr ' + str(stopFreq) + ' \n')
            sleep(1)

    def getStopFreq(self):
        '''
        Queries and returns stop frequency of sweep (Hz)
        '''

        self.fgen.write('spfr? \n')
        stopFreq = self.fgen.readline().rstrip()
        print 'Stop frequency of sweep set to: ', stopFreq, 'Hz'
        return stopFreq

    def setStartFreq(self,startFreq=1):
        '''
        Sets starting frequency of sweep.  Frequency must be greater than zero and less tan maximum frequency allowed by current function.  If start frequency is greater than stop frequency, a downward sweep from max to min frequency will be generated. 

        startFreq = starting frequency of sweep (Hz)
        '''
        if startFreq <= 0:
            print 'ERROR: Starting frequency must be greater than 0.'
            exit()
        else:
            self.fgen.write('stfr ' + str(startFreq) + ' \n')
            sleep(1)

    def getStartFreq(self):
        '''
        Queries and returns starting frequency of sweep (Hz)
        '''
        self.fgen.write('stfr? \n')
        startFreq = self.fgen.readline().rstrip()
        print 'Starting frequency of sweep set to: ', startFreq, 'Hz'
        return startFreq

    def setSweepSpan(self):
        '''
        Sets the start frequency to the start marker frequency and the stop frequency to the stop marker frequency.
        '''
        self.fgen.write('spmk \n')
        sleep(1)
        print 'Start and stop frequency set to corresponding marker frequencies.'
    def setTrigRate(self, trigRate=1):
        '''
        Sets the trigger rate for internally triggered single sweeps and bursts.  Rounded to 2 significant digits.  Range from 0.001 to 10 kHz.  
        
        trigRate = trigger rate for internally triggered single sweeps and bursts.
        '''
        if trigRate < 0.001 or trigRate > 10000:
            print 'ERROR: Trigger rate must be between 0.001 and 10000 Hz.'
            exit()
        else:
            self.fgen.write('trat ' + str(trigRate) + ' \n')
            sleep(1)
   
    def getTrigRate(self):
        '''
        Queries and return trigger rate (Hz) for internally triggered single sweeps and bursts.
        '''
        
        self.fgen.write('trat? \n')
        tRate = self.fgen.readline().rstrip()
        print 'Internal trigger rate set to: ',tRate , 'Hz'
        return tRate

    def setTrigSource(self,trigSource='single'):
        '''
        Sets the trigger source for bursts and sweeps.  

        trigSource = trigger source for bursts and sweeps.
        'single', 'internal', 'pos_ext' for positive slope external, 'neg_ext' for negative slope external, 'line'

        **NOTE: for single sweeps and bursts, the *TRG command triggers the sweep
        '''
        if trigSource == 'single':
            self.fgen.write('tsrc 0 \n')
        elif trigSource == 'internal':
            self.fgen.write('tsrc 1 \n')
        elif trigSource == 'pos_ext':
            self.fgen.write('tsrc 2 \n')
        elif trigSource == 'neg_ext':
            self.fgen.write('tsrc 3 \n')
        elif trigSource == 'line':
            self.fgen.write('tsrc 4 \n')
        else:
            print 'ERROR: invalid trigger source option'
            exit()
        sleep(1)

    def getTrigSource(self):
        '''
        Queries and returns trigger source
        '''
        self.fgen.write('tsrc? \n')
        trigSourceCheck = atoi(self.fgen.readline().rstrip())
        if trigSourceCheck == 0:
            tSource = 'single'
            print 'Trigger source set to single'
        elif trigSourceCheck == 1:
            tSource = 'internal'
            print 'Trigger source set to internal'
        elif trigSourceCheck == 2:
            tSource = 'positive slope external'
            print 'Trigger source set to positive slope external'
        elif trigSourceCheck == 3:
            tSource = 'negative slope external'
            print 'Trigger source set to negative slope external'
        elif trigSourceCheck == 4:
            tSource = 'line'
            print 'Trigger source set to line'
        return tSource

class Arbitrary(DS345):
    '''Arbitrary waveform and modulation commands'''

    def setArbModRate(self,rate=1):
        '''
        Sets the arbitrary modulation rate divider (rate at which arbitrary modulations are generated).  Range from 1 to 2^(23)-1.
        Arbitrary AM takes 0.3 microseconds/point, arbitrary FM takes 2 microseconds/point and aribtrary PM takes 0.5 microseconds/point.

        '''
        if rate < 1 or rate > (2**23-1):
            print 'ERROR: arbitrary modulation range must be between 1 and 2^(23)-1.'
            exit()
        else:
            self.fgen.write('amrt ' + str(rate) + ' \n')
            sleep(1)
            self.fgen.write('amrt? \n')
            print 'Arbitrary modulation rate set to: ', self.fgen.readline().rstrip(), 'Hz'

    def loadArbWaveform(self,datafile):
        '''
        Download arbitrary waveforms.  
        Waveform will first be plotted.  When figure is closed, data will be loaded to DS345.
        Each value should be in the range -2047 to 2047
        datafile = /path/to/filename.txt
        Data must also be in a single column, not a single row.
        Modified from: http://mesoscopic.mines.edu/acoustics-old/contrib/arb.py
        '''

        Modulate().enable()

        fd = open(datafile,'r')
        data = fd.readlines()
        plt.plot(data)
        plt.show()
        lengthData = len(data)
      
        checkSum = 0 # sent to the fgen after the data to ensure integrity
  
        for iDataItem in range(lengthData):
            data[iDataItem] = data[iDataItem].replace('\n','')
            data[iDataItem] = float(data[iDataItem])
            checkSum = int(checkSum + data[iDataItem])
        
        # Ask for data load permission, fgen returns '1' if it is ready
        self.fgen.write('ldwf?0'+',' + str(lengthData) +' \n')
        sleep(1)
        reply = self.fgen.readline()
     
        if atoi(reply) == 1:

            # DS345 is ready, send the data in 2 BYTE binary format
            for iDataItem in range(lengthData):
                self.fgen.write(pack('h',data[iDataItem]))

            # Send the checksum 
            self.fgen.write(pack('i',checkSum))
            sleep(1)
            print 'SUCCESS! done loading waveform data \n'
        else:
            print 'ERROR: unable to load waveform data \n'

    def loadModulationPattern(self,datafile,modType='AM'):
        ''' 
        Download arbitrary modulation patterns.  
        Waveform will first be plotted.  When figure is closed, data will be loaded to DS345.
        Modulation type (modType) must already be set to AM, FM, or PM. See  Modulate().setModType() 
        AM: 
        Values are a fraction of panel amplitude to be output.  Data length limited to 10000 points.  Values 0 to 32767 accepted (-32767 to 32767 for DSBSC).
        FM:
        Values are the frequency to be output.  32 bit int values accepted, where value = 2**(32)*(frequency/40 MHz) 
        PM:
        Values are phase shift to be made relative to the current phase.  Values must be between -180 and 180 deg.  Value = 2**(31)*(phase shift/180 deg).  Negatives must be in 2's complement format.

        Number of points is limited to 10000 AM points, 1500 FM points, and 4000 PM points.  
        datafile = /path/to/filename.txt
        '''
        
        Modulate().enable()
        Modulate().setModWaveform(modType='arb')
        Modulate().setModType(modType)

        fd = open(datafile,'r')
        data = fd.readlines()
        lengthData = len(data)
        
        checkSum = 0 # sent to the fgen after the data to ensure integrity
        
        plt.plot(data)
        plt.plot()

        for iDataItem in range(lengthData):
            data[iDataItem] = data[iDataItem].replace('\n','')
            data[iDataItem] = int(data[iDataItem])
            checkSum = int(checkSum + data[iDataItem])
       
        # Ask for data load permission, fgen returns '1' if it is ready
        self.fgen.write('amod? ' + str(lengthData) +' \n')
        
        reply = self.fgen.readline()
        
        if atoi(reply) == 1:

            # DS345 is ready, send the data in 2 BYTE binary format
            if modType == 'AM':
                if len(data) > 10000:
                    print 'Length of data too long! For AM: use less than 10,000 points'
                for iDataItem in range(lengthData):
                    self.fgen.write(pack('H',data[iDataItem]))
                
            elif modType == 'FM':
                if len(data) > 1500:
                    print 'Length of data too long! For FM: use less than 1500 points'
                for iDataItem in range(lengthData):
                    self.fgen.write(pack('I',data[iDataItem]))
             
            elif modType == 'PM':
                if len(data) > 4000:
                    print 'Length of data too long! For PM: use less than 4000 points'
                for iDataItem in range(lengthData):
                    self.fgen.write(pack('i',data[iDataItem]))
                
            # Send the checksum 
            self.fgen.write(pack('i',checkSum))
            sleep(1)
            print 'SUCCESS!: done loading waveform data \n'
        else:
            print 'ERROR: unable to load waveform data \n'

class Status(DS345):
    '''Get and set various status registers'''

    def clearStatus(self):
        '''
        Clears all status registers
        '''
        self.fgen.write('*CLS \n')
        sleep(1)
        print 'All status registers cleared.'

    def setStatus(self, statValue=0):
        '''
        Sets standard event status byte enable register to value specified by statValue.
        '''
        self.fgen.write('*ESE ' + str(statValue) + ' \n')
        sleep(1)
        print 'Event status byte enable register set to: ', str(statValue)

    def getStatus(self, statValue=0):
        '''
        Reads value of standard event status register. If statValue is specified, the value of statValue is returned (0 or 1).

        Reading this register will clear it while reading statValue will clear just statValue.
        '''
        if statValue == 0:
            self.fgen.write('*ESR? 0 \n')
        elif statValue == 1:
            self.fgen.write('*ESR? 1 \n')
        else:
            self.fgen.write('*ESR? \n')
        sleep(1)
        status = self.fgen.readline().rstrip()
        print 'Value of standard event status register is: ', status
        return status

    def setPowerStatus(self,powerStat=0):
        '''
        Sets the value of the power-on status clear bit.  If powerStat = 1, all status and enable registers are cleared on power up.  If powerStat = 0, the status enable registers maintain their values at power down.  Allows production of a service request at power up. 
        '''
        if powerStat == 0:
            self.fgen.write('*PSC 0 \n')
        elif powerStat == 1:
            self.fgen.write('*PSC 0 \n')

        self.fgen.write('*PSC? \n')
        sleep(1)
        print 'Power-on status set to: ', self.fgen.readline().rstrip()
        
    def setPollReg(self,polValue=0):
        '''
        Sets the serial poll enable register to the decimal
value of the parameter polValue.
        '''
        self.fgen.write('*SRE ' + str(polValue) + ' \n')
        sleep(1)
        self.fgen.write('*SRE? \n')
        print 'Serial poll enable register set to: ', self.fgen.readline().rstrip()

    def getSerialPoll(self,polByte='none'):
        '''
        Reads the value of the serial poll byte.  If polByte is specified, the value of polByte is returned (0 or 1). Reading this register
has no effect on its value as it is a summary of the other status registers.
        '''
        if polByte == 0:
            self.fgen.write('*STB? 0 \n')
        elif polByte == 1:
            self.fgen.write('*STB? 1 \n')
        elif polByte == 'none':
            self.fgen.write('*STB? \n')
        sleep(1)
        byte = self.fgen.readline().rstrip()
        print 'Serial poll byte read as: ', byte
        return byte

    def setDDSReg(self,DValue=0):
        '''
        Sets the DDS status enable register to DValue.
        '''
        self.fgen.write('DENA ' + str(DValue) + ' \n')
        sleep(1)
        self.fgen.write('DENA? \n')
        print 'DDS status enable register set to: ', self.fgen.readline().rstrip()

    def getDDSstat(self, DByte=0):
        '''
        Reads and returns the value of the DDS status byte.  If DByte is specified, the value of DByte is returned.  Reading this register will clear it, while reading DByte will clear just DByte.
        '''
        self.fgen.write('STAT? ' + str(DByte) + ' \n')
        sleep(1)
        status = self.fgen.readline().rstrip()
        print 'Value of DDS status byte', str(DByte), ' is: ', status
        return status

class Test(DS345):
    '''Run tests or get measurements'''

    def selfTest(self):
        '''
        Runs the DS345 internal self-tests.  After tests are complete, the test status is returned. 
        '''
        self.fgen.write('*TST? \n')
        reply = ''
        print 'Running self-tests...'
        while reply == '':
            reply = self.fgen.readline().rstrip()
            sleep(1)
            print '...'
        
        reply = atoi(reply)
        if reply == 0:
            print 'PASSED: Self tests successfully completed.'
        elif reply == 1: 
            print 'CPU Error. The DS345 has detected a problem in its CPU.'
            exit()
        elif reply == 2:
            print 'Code Error. The DS345s ROM firmware has a checksum error.'
            exit()
        elif reply == 3:
            print 'Sys RAM Error. The system RAM failed its test.'
            exit()
        elif reply == 4:
            print 'Cal Data Error. The DS345s calibration data has become corrupt.'
            exit()
        elif reply == 5:
            print 'Function Data Error. The waveform RAM failed its test.'
            exit()
        elif reply == 6:
            print 'Program Data Error. The modulation program RAM failed its test.'
            exit()
        elif reply == 7:
            print 'Trigger Error. The trigger detection circuits failed their test.'
            exit()
        elif reply == 8:
            print 'A/D D/A Error. Either the A/D or one of the D/As failed its test. The front panel message is more specific.'
            exit()
        elif reply == 9:
            print 'Signal Error. Either the waveform DAC, amplitude control, or the output amplifier has failed.'
            exit()
        elif reply == 10:
            print 'Sync Error. The sync signal generator has failed.'
            exit()
        elif reply == 11:
            print 'Doubler Error. The frequency doubler has failed.'
            exit()

    def getAnalogVoltage(self,channel=1,dataType='raw'):
        '''
        Usees the DS345 A/D converter to measure the voltage on specified channel.
        channel = specify channel
        dataType = 'raw' for raw data value, 'offset' for value corrected for the A/D's offset, and 'offset_gain' for value corrected for the A/D's offset and gain errors.
        '''
        if dataType == 'raw':
            self.fgen.write('$ATD? ' + str(channel) + ',0 \n')
            sleep(1)
            value = self.fgen.readline().rstrip()
            print 'Raw voltage on channel ', str(channel), ' is: ', str(value)
        elif dataType == 'offset':
            self.fgen.write('$ATD? ' + str(channel) + ',1 \n')  
            sleep(1)
            value = self.fgen.readline().rstrip()
            print 'Voltage on channel ', str(channel), ' corrected for offset is: ' + str(value)
        elif dataType == 'offset_gain':
            self.fgen.write('$ATD? ' + str(channel) + ',2 \n')  
            sleep(1)
            value = self.fgen.readline().rstrip()
            print 'Voltage on channel ', str(channel), ' corrected for offset and gain errors is: ', str(value)
        else:
            print 'ERROR: invalid data type.'

        return value
  

class Calibrate(DS345):
    '''Calibration functions for DS345'''

    def routines(self):
        '''
        Returns the DS345's self calibration routines.  When calibration is compelte, the status of the calibration is returned.  
        '''
        self.fgen.write('*CAL? \n')
        reply = ''
        print 'Running self-calibration routines...'
        while reply == '':
            reply = self.fgen.readline().rstrip()
            sleep(1)
            print '...'

        reply = atoi(reply)
       
        if reply == 0:
            print 'PASSED: Self calibration successfully completed'
        elif reply == 1:
            print 'ERROR: DS345 not warmed up. At least 2 minutes must elapse between power on and calibration.'
            exit()
        elif reply == 2:
            print 'ERROR: Self-Test Fail. The DS345 must pass its self tests before calibration.'
            exit()
        elif reply == 3:
            print 'A/D Cal Error. The DS345s A to D converter could not be calibrated.'
            exit()
        elif reply == 4:
            print 'DC Offset Fail. The DS345 was unable to calibrate its DC offset.'
            exit()
        elif reply == 5:
            print 'Amplitude Cal Fail. The DS345 was unable to calibrate its amplitude control circuitry.'
            exit()
        elif reply == 6:
            print 'Doubler Cal Fail. The DS345 was unable to calibrate the doubler offset or the gain of the doubler/square wave signal path.'
            exit()

    def setAttenuators(self,range=0):
        '''
        Sets output attenuators range.  Range must be between 0dB to 42 dB in 6 dB steps.  Choose: 0, 6, 12, 18, 24, 30, 36, or 42.
        '''
        if range == 0:
            self.fgen.write('$ATN 0 \n')
        elif range == 6:
            self.fgen.write('$ATN 1 \n')
        elif range == 12:
            self.fgen.write('$ATN 2 \n')
        elif range == 18:
            self.fgen.write('$ATN 3 \n')                       
        elif range == 24:
            self.fgen.write('$ATN 4 \n')
        elif range == 30:
            self.fgen.write('$ATN 5 \n')
        elif range == 36:
            self.fgen.write('$ATN 6 \n')
        elif range == 42: 
            self.fgen.write('$ATN 7 \n')
        Calibrate().getAttenuators()

    def getAttenuators(self):
        '''
        Gets output attenuators range.  Returned in dB
        '''
        self.fgen.write('$ATN? \n')
        sleep(1)
        reply = atoi(self.fgen.readline().rstrip())

        if reply == 0:
            att = 0
            print 'Attenuators range set to 0 dB'
        elif reply == 1: 
            att = 6
            print 'Attenuators range set to 6 dB'
        elif reply == 2:
            att = 12
            print 'Attenuators range set to 12 dB'
        elif reply == 3:
            att = 18
            print 'Attenuators range set to 18 dB'
        elif reply == 4:
            att = 24
            print 'Attenuators range set to 24 dB'
        elif reply == 5:  
            att = 30
            print 'Attenuators range set to 30 dB'
        elif reply == 6:
            att = 36
            print 'Attenuators range set to 36 dB'
        elif reply == 7:
            att = 42
            print 'Attenuators range set to 42 dB'
        return att

    def setFactoryCalib(self):
        '''
        Returns factory calibration bytes.  An error is returned if calibration is not enabled.
        '''
        self.fgen.write('$FCL \n')
        sleep(1)
        reply = self.fgen.readline().rstrip()
        return reply

    def setMimicDAC(self, value):
        '''
        Sets the mimic DAC to specified value (0 to 255). If the DS345 has modulation enabled, this command will have no effect.
        '''
        if value < 0 or value > 255:
            print 'Invalid value for mimic DAC.  Choose a value between 0 and 255.'
        self.fgen.write('$MDC ' + str(value) + ' \n')
        sleep(1)

    def setCalWord(self, j=0,k=0):
        '''
        Set shte value of calibration word j to k.  j may have a value between 0 to 509, while k may range from -32768 to +32767.  This command will generate an error if calibration is not enabled.

        **NOTE: this command will alter the calibration of the the DS345. To correct the calibration the factory calibration bytes may be recalled (see the getFactoryCalib function).
        '''
        if j < 0 or j > 509:
            print 'Invalid value for word j. Choose a value between 0 and 509.'
        if k < -32768 or k > 32768:
            print 'Invalid value for word k. Choose a value between -32768 and +32768.'
        else:
            self.fgen.write('$WRD ' + str(j) + ',' + str(k) + ' \n')
        sleep(1)
        Calibrate().getCalWord()
        
    def getCalWord(self):
        '''
        Queries and returns calibration word j to k
        '''
        self.fgen.write('$WRD? \n')
        sleep(1)
        print self.fgen.readline().rstrip()
 
            
