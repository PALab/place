"""Stanford Research Systems SR850 DSP Lock-In Amplifier"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .sr850_interface import SR850Interface

class SR850(Instrument):
    """PLACE module for controlling the SRS SR850 lock-in amplifier."""
    def __init__(self, config, plotter):
        """Constructor"""
        Instrument.__init__(self, config, plotter)

    def config(self, metadata, total_updates):
        """Configure the amplifier.

        Typically, the amplifier will be configured at the beginning of an
        experiment, so the majority of the activity will happen in this method.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__,
                                                     'serial_port', '/dev/ttys0')
        metadata['sr850_settings'] = {
            'serial_port': serial_port,
            }

    def update(self, update_number):
        """Perform updates to the amplifier during an experiment.

        All settings are set during the config phase, so this method does not
        currently do anything.

        :param update_number: the current update count
        :type update_number: int
        """
        pass

    def cleanup(self, abort=False):
        """Cleanup the amplifier.

        Nothing to cleanup.

        :param abort: indicates the experiment is being aborted rather than
                      having finished normally
        :type abort: bool
        """
        pass

    def serial_port_query(self, serial_port, field_name):
        """Query if the instrument is connected to serial_port

        :param serial_port: the serial port to query
        :type metadata: string

        :returns: whether or not serial_port is the correct port
        :rtype: bool
        """

        try:
            sr_amp = SR850Interface(serial_port)
            dev_config = sr_amp.idn()
            dev_config = sr_amp.idn()  #Try it twice to eliminate errors from previous attempts on this port
            if 'SR850' in dev_config:
                return True
            return False
        except (serial.SerialException, serial.SerialTimeoutException):
            return False