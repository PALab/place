import numpy as np
import matplotlib.pyplot as plt
from math import sin

'''
Here are a few example waveforms that can be loaded to DS345
with the DS345_driver module and functions: 
Arbitrary().loadArbWaveform() and Arbitrary().loadModulationPattern()

Created August 21, 2014
@author: Jami L Johnson
'''

x_array = range(0,1000)
y_array = [abs(int(x*sin(x))) for x in x_array]
print type(y_array[0])
plt.plot(x_array,y_array)
plt.show()

# for Arbitrary().loadArbWaveform()
np.savetxt('waveform.txt',y_array)
data = np.loadtxt('waveform.txt')

 #for Arbitrary().loadModulationPattern() where modType = 'AM' or 'FM'
np.savetxt('waveform.txt',y_array,fmt='%h')
data = np.loadtxt('waveform.txt',dtype='int')
print type(data[0])
print data[0]

# for Arbitrary().loadModulationPattern() where modType = 'PM'
data2 = np.array([-180, -90, 0, 90, 180])
np.savetxt('phase.txt',data2,fmt='%i')
