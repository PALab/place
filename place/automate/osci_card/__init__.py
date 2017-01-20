"""
This package allows data acquisition with an Alazar oscilloscope card.

The controller module provides classes that can be used to initialize,
configure and record.  An Alazar command library is required, and must
be obtained from Alazar Tech when the card is purchased. The library
should be saved as AlazarCmd.py in the osci_card folder to be imported
by the controller module.

See the documentation of the controller module for more details(print
osciCard.controller.__doc__). The remaining modules are used by the
controller module or are used for testing.
"""
import os
constantHeader = '/usr/local/AlazarTech/include/AlazarCmd.h'
constantFileName = os.path.join(os.path.dirname(__file__), "AlazarCmd.py")
try:
    from . import AlazarCmd as cons
except ImportError:
    if os.path.isfile(constantHeader):
        from .parseConstants import parseHeader
        parseHeader(constantHeader, constantFileName)
        from . import AlazarCmd as cons
from .controller import (
        BasicController,
        ContinuousController,
        TriggeredContinuousController,
        TriggeredRecordingController,
        TriggeredRecordingSingleModeController
        )
__all__ = [
        'BasicController',
        'ContinuousController',
        'TriggeredContinuousController',
        'TriggeredRecordingController',
        'TriggeredRecordingSingleModeController'
        ]

