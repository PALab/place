from time import sleep
from pypal.automate.function_generator.DS345_driver import Generate, Modulate, Arbitrary, Status, Setup, Test, Calibrate

''' 
Example functions that can be used to test communication with Stanford Research Systems DS345 function generator.  It is recommended to check output of function generator and front panel response when using these commands.

Created August 21, 2014 
@author Jami L Johnson
'''

# setup serial connection parameters
Setup()

# open connection to DS345
Setup().openConnection()


# get ID information for DS345
#ID = Status().getID()
#print ID

# set to default settings
Setup().setDefault() # initialize default settings 

# set parameters of output function
#Generate().functOutput(amp=1,ampUnits='VP',freq=10000,sampleFreq=1,funcType='square',invert='on',offset=2,phase=10,aecl='n',attl='n')

# save current parameters to number 1
#Setup().saveSettings(setNum=1)
#sleep(1)
#Setup().getSettings(setNum=1)
#sleep(1)

#Modulate().enable() # must do this before using any Modulate() commands
#Modulate().setBurstCount(burstCount=20)
#print Modulate().getBurstCount()
#Modulate().setAMDepth(depth=20)
#print Modulate().getAMDepth()
#Modulate().setFMSpan(span=500)
#print Modulate().getFMSpan()
#Modulate().setModWaveform(modType='triangle')
#Modulate().setSweepExtreme()
#Setup().setDefault()
#sleep(4)
#Modulate().setModWaveform(modType='single') ##FIX THIS!!
#sleep(5)
#print Modulate().getModWaveform()
#Modulate().setSweepFreq(markerType='start',markerFreq=100)
#print Modulate().getSweepFreq(markerType='start')
#Modulate().setModType(modType='linear')
#print Modulate().getModType()
#Modulate().setPhaseMod(modPhase=100)
#print Modulate().getPhaseMod()
#Modulate().setModRate(modRate = 500)
#print Modulate().getModRate()
#Modulate().setSpanFreq(spanFreq=10)
#print Modulate().getSpanFreq()
#Modulate().setStopFreq(stopFreq=10)
#print Modulate().getStopFreq()
#Modulate().setSpanFreq(spanFreq=100)
#Modulate().setStartFreq(startFreq=5)
#Modulate().getStartFreq()
#Modulate().setTrigRate(trigRate=5)
#print = Modulate().getTrigRate()
#Modulate().setTrigSource(trigSource='pos_ext')
#print Modulate().getTrigSource()
#Arbitrary().setArbModRate(rate=5)

#Status().getStatus(statValue=1)
#Status().getDDSstat()

Test().selfTest() # run basic self tests
#Test().getAnalogVoltage(channel=2,dataType='offset_gain')

Calibrate().routines() # run factory calibration routine
#Calibrate().setAttenuators(range=42)
#att = Calibrate().getAttenuators()
#print att
#Calibrate().setFactoryCalib()

#Arbitrary().loadArbWaveform('waveform.txt')
#Arbitrary().loadModulationPattern('waveform.txt',modType='AM')
Setup().closeConnection()
