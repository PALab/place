"""QuantaRay module for PLACE"""
from time import sleep
from place.plugins.instrument import Instrument
from .qray_driver import QuantaRay

class QuantaRayOn(Instrument):
    """Device class for turning ON the laser"""

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
        sleep(20)
        QuantaRay().single_shot()
        QuantaRay().normal_mode()
        QuantaRay().set_osc_power(self._config['power_percentatge'])
        sleep(1)
        metadata['oscillator_power'] = QuantaRay().get_osc_power()
        metadata['repeat_rate'] = QuantaRay().get_trig_rate()

    def update(self, update_number):
        """This is where the laser gets turned on to repeat.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int
        """
        QuantaRay().repeat_mode(self._config['watchdog_time'])
        sleep(1)

    def cleanup(self, abort=False):
        """Turn off the laser here since this will happen earlier in the
        cleanup process than the cleanup function in QuantaRayOff.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool
        """
        QuantaRay().turn_off()
        QuantaRay().close_connection()


class QuantaRayOff(Instrument):
    """Device class for turning OFF the laser"""

    def config(self, metadata, total_updates):
        """Configuration of laser is done by the QuantaRayOn class.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        pass

    def update(self, update_number):
        """This is where the laser gets set back to single shot.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int
        """
        QuantaRay().single_shot()
        QuantaRay().set_watchdog(time=0) # disable watchdog

    def cleanup(self, abort=False):
        """Cleanup is performed by the QuantaRayOn class.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool
        """
        pass
