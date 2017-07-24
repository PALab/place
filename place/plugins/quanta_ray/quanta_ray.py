"""QuantaRay module for PLACE.

This module is designed to automate the process of turning the INDI laser on at
the start of an experiment and turn it off at the end of the experiment.
"""
from time import sleep
from place.plugins.instrument import Instrument
from .qray_driver import QuantaRay

class QuantaRayINDI(Instrument):
    """Device class for the QuantaRay INDI laser.

    .. warning:: This automated module is not intended to replace any existing
        safety procedures. Please exercise caution so that unexpected behavior
        by this module does not pose a safety risk to yourself or others.

    This class provides *very basic* automation of the INDI laser. The laser is
    turned on at the start of the experiment and it is not turned off until the
    cleanup method is called (typically at the end of an experiement).

    The watchdog parameter can (and should) be used as a safety precaution, but
    understand that if the other steps of the experiment exceed the watchdog
    time, the laser will shut off, likely aborting the experiment. Therefore,
    in situations where the other steps of the experiment exceed 110 seconds
    (the watchdog maximum), the watchdog can be disabled by setting it to 0.
    However, please exercise extra caution when operating the laser without a
    watchdog, as a program error could cause the laser to run continuously
    until manually turned off.

    QuantaRayINDI requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    power_percentage          int            the power setting for the laser
    watchdog_time             int            the maximum number of seconds other tasks can
                                             be performed before the next laser command must
                                             be issued, or zero to disable watchdog
    ========================= ============== ================================================

    QuantaRayINDI will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    oscillator_power          int            the oscillator power level returned from the
                                             device
    repeat_rate               int            the repeat rate of laser pulses
    ========================= ============== ================================================

    QuantaRayINDI does not produce any experimental data.
    """

    def config(self, metadata, total_updates):
        """Configure the laser - turning off watchdog until repeat mode is
        selected.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        QuantaRay().open_connection()
        QuantaRay().set_watchdog(time=0) # disable watchdog for now
        QuantaRay().turn_on()
        print('...waiting 20 seconds for laser to turn on...')
        sleep(20)
        QuantaRay().single_shot()
        QuantaRay().normal_mode()
        QuantaRay().set_osc_power(self._config['power_percentatge'])
        sleep(1)
        metadata['oscillator_power'] = QuantaRay().get_osc_power()
        metadata['repeat_rate'] = QuantaRay().get_trig_rate()
        QuantaRay().repeat_mode(self._config['watchdog_time'])
        QuantaRay().close_connection()

    def update(self, update_number):
        """Do nothing. But send a command to the laser to reset the watchdog.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int
        """
        QuantaRay().open_connection()
        QuantaRay().get_status()
        QuantaRay().close_connection()

    def cleanup(self, abort=False):
        """Turn off the laser.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool
        """
        QuantaRay().open_connection()
        QuantaRay().single_shot()
        sleep(1)
        QuantaRay().turn_off()
        QuantaRay().close_connection()
