"""
This package allows the data acquisition with an Alazar oscilloscope card. 

The controller module provides classes that can be used to initialize, configure and record. 
See the documentation of the controller module for more details(print osciCard.controller.__doc__). The remaining modules are used by the 
controller module or are used for testing. 
"""
from controller import BasicController, ContinuousController, TriggeredContinuousController, TriggeredRecordingController, TriggeredRecordingSingleModeController
__all__ = ['controller']