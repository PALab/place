"""
This module allows RS-232 interfacing with Polytec OFV-5000 controller and OFV-505 sensor head.  

See the documentation of the vibrometer module for more details (print polytec.vibrometer.__doc__).
 
@author: Jami L Johnson
"""
from .vibrometer import Polytec, PolytecController,  PolytecInterface, PolytecSensorHead, PolytecDecoder

__all__ = ['vibrometer']
