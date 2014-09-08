'''
General functions for laser-ultrasound scans using PLACE automation.  Functions to initialize instruments, perform common intstrument functions, as well as initialize header.

@author: Jami L Johnson
September 8, 2014
'''
class initialize:

    def Polytec(portPolytec, baudPolytec, decoder, drange):
        '''Initialize Polytec vibrometer and obtain relevant settings to save in trace headers. Also autofocuses vibrometer.'''
        # set decoder range
        Polytec(portPolytec, baudPolytec).openConnection() #runs __init__ and opens serial connection
        PolytecDecoder().setRange(decoder, drange)

        # calculate delay due to decoder
        delayString = PolytecDecoder().getDelay(decoder)
        delay =  re.findall(r'[-+]?\d*\.\d+|\d+', delayString) # get time delay in us
        timeDelay =  float(delay[0])

        # get maximum frequency recorded
        freqString = PolytecDecoder().getMaxFreq(decoder)
        freq =  re.findall(r'[-+]?\d*\.\d+|\d+',freqString)
        delNumF = len(freq)+2
        freq = float(freq[0])
        freqUnit = freqString[delNumF:].lstrip()
        freqUnit = freqUnit.rstrip()
        if freqUnit=='kHz':
            multiplier = 10**3
        elif freqUnit == 'MHz':
            multiplier = 10**6
        maxFreq = freq*multiplier
  
        # get range of decoder and amplitude calibration factor
        decoderRange = PolytecDecoder().getRange(decoder)
        rangeNum = re.findall(r'[-+]?\d*\.\d+|\d+',decoderRange) 
        delNumR = len(rangeNum)+1
        calib = float(rangeNum[0])
        calibUnit = decoderRange[delNumR:].lstrip()

        # autofocus vibrometer
        PolytecSensorHead().autofocusVibrometer()

        return timeDelay, maxFreq, calib, calibUnit

    def OsciCard(channel, vibChannel, sampleRate, duration, averagedRecords, trigLevel, trigRange, channelRange, ACcouple, ohms):
        '''Initialize Alazar Oscilloscope Card.'''

        # initialize channel for signal from vibrometer decoder
        control = card.TriggeredRecordingController()  
        control.configureMode = True
        control.createInput(channel=channel,inputRange=channelRange, AC=ACcouple, impedance=ohms)
        control.setSampleRate(sampleRate)  
        samples = control.samplesPerSec*duration*10**-6 
        samples = int(pow(2, ceil(log(samples,2)))) # round number of samples to next power of two
        control.setSamplesPerRecord(preTriggerSamples=0,postTriggerSamples=samples)
        control.setRecordsPerCapture(averagedRecords)
        triggerLevel = 128 + int(127*trigLevel/trigRange)
        control.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
        control.setTriggerTimeout(10)  
        configureMode = False    

        # initialize channel for vibrometer sensor head signal
        vibSignal = card.TriggeredContinuousController()
        vibSignal.configureMode=True
        vibSignal.createInput(channel=vibChannel,inputRange='INPUT_RANGE_PM_4_V', AC=False, impedance=ohms) # 0 to 3 V DC
        vibSignal.setSamplesPerRecord(preTriggerSamples=0,postTriggerSamples=1)
        vibSignal.setRecordsPerCapture(3)
        vibSignal.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
        vibSignal.setTriggerTimeout(10)

        print 'oscilloscope card ready and parameters set'
        return samples, control, vibSignal
                
    def Controller(GroupName, Positioner, xi):
        '''Initialize XPS controller and move to stage to starting scan position'''
        xps = XPS()
        xps.GetLibraryVersion()

        socketId = xps.TCP_ConnectToServer("130.216.55.92",5001,3) # connect over network
        print "connected to: ", socketId

        ControllerErr = xps.ControllerStatusGet(socketId)
        if ControllerErr[0] == 0:
            print 'XPS controller status: ready'
        else:
            print 'XPS controller status failed: ERROR =', ControllerErr

        LogErr =  xps.Login(socketId, "Administrator", "Administrator")
        if LogErr[0] == 0:
            print 'login successful'
        else:
            print 'login failed: ERROR = ', LogErr

        xps.GroupKill(socketId, GroupName)
        InitializeGrpErr = xps.GroupInitialize(socketId, GroupName)
        if InitializeGrpErr[0] == 0:
            print 'group initialized'
        else:
            print 'group initialize failed: ERROR = ', InitializeGrpErr
        xps.GroupStatusGet(socketId, GroupName)
    
        HomeErr = xps.GroupHomeSearch(socketId, GroupName)
        if HomeErr[0] == 0:
            print 'home search successful'
        else:
            print 'home search failed: ERROR = ', HomeErr

        xps.GroupMoveAbsolute(socketId, GroupName, [xi])
        ck = 0 
        actualPos =  xps.GroupPositionCurrentGet(socketId, GroupName,1)

        print 'XPS stage initialized'

        return GroupName, xps, socketId
    
    def QuantaRay():
        ''' Starts Laser in rep-rate mode and sets watchdog time.  Returns the repitition rate of the laser.'''

        QuantaRay().openConnection()
        QSW().set(cmd='REP') # set to rep rate: stage will already be in starting position
    
        repRate = QRread().getTrigRate()
        repRate = re.findall(r'[-+]?\d*\.\d+|\d+',repRate) # get number only
        repRate = float(repRate[0])

        QRcomm().setWatchdog(time=ceil(2*traceTime)) # set watchdog time > time of one trace, so laser doesn't turn off

        return repRate

    def Header(totalTraces=1, averagedRecords=1, channel='', ohms='50', receiver='null', decoder='null', drange='5mm', timeDelay=0, energy=0, maxFreq='20MHz', minFreq='0Hz', position=0, unit='mm', source_unit='rad', source_position=0,calib=1, calibUnit='V', comments=''):

        '''Initialize generic trace header for all traces'''

        custom_header = Stats()
        if ohms == 1:
            impedance = '1Mohm'
        else:
            impedance = '50 ohms'
        custom_header.impedance = impedance
        custom_header.max_frequency = maxFreq
        custom_header.receiver = receiver
        custom_header.decoder = decoder
        custom_header.decoder_range = drange
        custom_header.source_energy = energy
        custom_header.position = position
        custom_header.position_unit = unit
        custom_header.source_position = source_position
        custom_header.source_unit = source_unit
        custom_header.comments = comments
        custom_header.averages = averagedRecords
        custom_header.calib_unit = calibUnit
        custom_header.time_delay = timeDelay
        custom_header.scan_time = ''
        custom_header.focus = 0

        header = Stats(custom_header)
        if receiver == 'polytec':
            if decoder == 'DD-300' and ohms == 1:
                header.calib = 25
            else:
                header.calib = calib
        header.channel = channel
        
        return header

class checks:

    def checkVibrometer(channel, vibSignal, sigLevel):
        ''' 
        Checks focus of vibrometer sensor head and autofocuses if less then sigLevel specified (0 to ~1.1)
        channel = channel "signal" from polytec controller is connected to on oscilloscope card
        vibSignal = 
        ''' 
        vibSignal.startCapture()
        vibSignal.readData()
        signal = vibSignal.getDataRecordWise(channel)
        signal = np.average(signal,0)

        k = 0
        while signal < sigLevel:
            print 'sub-optimal focus:'
            if k == 0:
                PolytecSensorHead().autofocusVibrometer(span='Small')
            elif k == 1:
                PolytecSensorHead().autofocusVibrometer(span='Medium')
            else: 
                PolytecSensorHead().autofocusVibrometer(span='Full')
                vibSignal.startCapture()
                vibSignal.readData()
                signal = vibSignal.getDataRecordWise(channel)
                signal = np.average(signal,0)
            k+=1
            if k > 3:
                print 'unable to obtain optimum signal'
                break
            
            return signal
