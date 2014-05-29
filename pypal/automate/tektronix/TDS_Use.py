'''
Example usage of Tektronix.TEK_driver module.  

@author: Jami L Johnson
Created May 27, 2014
'''
 
import TEK_driver
import numpy as np
import matplotlib.pyplot as plt 
from obspy import read, Trace, UTCDateTime
from obspy.core.trace import Stats
from obspy.core import AttribDict
import re
import h5py
import obspyh5
import sys
import os

sys.path.append('/home/jami/LabSoftware/') # directory that python should search for Python packages
os.system('export LD_LIBRARY_PATH=/usr/lib/mpich2/lib')
os.system('export PYTHONPATH=/home/jami/LabSoftware') 

scope = TEK_driver.TDS3014b(ip_addr='130.216.54.95')
header, data = scope.getWaveform(channel=1, format='counts')

print 'connected to: ', scope.getIDN()

ti = float(header['XZERO'])
tx = float(header['XINCR'])
tf = ti + (len(data) * tx)
t = np.arange(ti, tf, tx)

# plot data
plt.plot(t, data)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.show()

# create stream and save in H5 format
data = np.array(data)
trace = Trace(data=data,header=header)
trace.write('tekfile.h5','H5',mode='a')

