"""
This module can be used for Ethernet communication with Tektronix
TDS3014B oscilloscope.

See the documentation of the TEK_driver module for more details
(print Tektronix.TEK_driver.__doc__).
 
@author: Jami L Johnson
"""

import httplib2
from . import iri2uri
from .TEK_driver import TDS3014b

__all__ = ['TDS3014b']

