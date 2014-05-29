'''
Program that calls functions in pypal.analysis.PALplots.  See documentation in PALplots.py for details of each function.

@author: Jami L Johnson
Created May 29, 2014
'''
from obspy.core import read
from obspy import Stream
from pypal.analysis.PALplots import wiggle, contour, fk, fkfilter

stream = read('mydata.h5', format='H5', apply_calib=True)

wiggle(stream, percent=50)
contour(stream)
fk(stream)
fkfilter(stream,spread=7,colormap='gray')
