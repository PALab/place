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

