"""QuantaRay module for PLACE.

This module is designed to automate the process of turning the INDI laser on at
the start of an experiment and turn it off at the end of the experiment.
"""
import sys
from time import sleep
import threading
import numpy as np
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
    watchdog_time             int            the maximum number of seconds other tasks can
                                             be performed before the next laser command must
                                             be issued, or zero to disable watchdog
    power_mode                str            whether or not the power is varied across updates,
                                             either "const_power" or "var_power" for a constant
                                             or variable power, respectively
    start_power_percentage    int            the power setting for the laser at update 0 (and
                                             all updates if power_mode == "const_power")
    end_power_percentage      int            the power setting for the laser at the final update
                                             the power is increased or decreased linearly over the
                                             updates to get to this final value
    specify_shots             bool           True if the number of shots per update and the time 
                                             between them is to be controlled. If False, the laser
                                             will just run in continuous rep mode
    number_of_shots           int            the number of shots per update. 
                                             Applies only if specify_shots == True
    shot_interval             float          the time between individual shots (min 0.1 s)
                                             Applies only if specify_shots == True
    ========================= ============== ================================================

    QuantaRayINDI will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    oscillator_power          int            the oscillator power level returned from the
                                             device
    repeat_rate               int            the repeat rate of laser pulses
    ========================= ============== ================================================

    The QuantaRayINDI will produce the following experimental data:

    +---------------+-------------------------+---------------------------+
    | Heading       | Type                    | Meaning                   |
    +===============+=========================+===========================+
    | osc_power     | float                   | the oscillator power level|
    |               |                         | recorded from the laser   |
    +---------------+-------------------------+---------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``osc_power`` will be recorded as ``QuantaRayINDI-signal`` when using
        the QuantaRay INDI laser. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.
    """

    def __init__(self, config, plotter):
        """Constructor"""
        Instrument.__init__(self, config, plotter)
        self.power_increment = 0

    def config(self, metadata, total_updates):
        """Configure the laser - turning off watchdog until repeat mode is
        selected.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        QuantaRay().open_connection()
        QuantaRay().set_watchdog(time=0)  # disable watchdog for now

        self._start_laser()

        sleep(1)
        metadata['oscillator_power'] = QuantaRay().get_osc_power()
        metadata['repeat_rate'] = QuantaRay().get_trig_rate()

        if not self._config['specify_shots']:
            QuantaRay().close_connection()

        if self._config["power_mode"] == "var_power" and total_updates > 1:
            start_power = self._config['start_power_percentage']
            end_power = self._config['end_power_percentage']
            if start_power < end_power:
                self.power_increment = (min(100,end_power) - max(0,start_power)) / (total_updates - 1)
            else:
                self.power_increment = -1 * (min(100,start_power) - max(0,end_power)) / (total_updates - 1)

    def update(self, update_number, progress):
        """If normal rep mode, do nothing. But send a command to the laser 
        to reset the watchdog. If the power mode is variable, change the 
        oscillator power. If the shot number and interval have been
        set, control the triggering of the laser.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: progress data that is sent to the web app
        :type progress: dict

        :returns: an array containing the oscillator power level
        :rtype: numpy.array dtype='uint64'
        """

        QuantaRay().open_connection()

        if 'Oscillator simmer is on' not in str(QuantaRay().get_status()):
            self._start_laser()

        if self._config["power_mode"] == "var_power" and update_number > 0:
            QuantaRay().set_osc_power(self._config['start_power_percentage'] + (update_number * self.power_increment) )
            sleep(1)

        osc_power = float(QuantaRay().get_osc_power().split(' ')[0])

        if self._config['specify_shots']:
            thread = threading.Thread(target=self._control_shots, args=(self._config["number_of_shots"], self._config["shot_interval"]),daemon=True)
            thread.start()
        else:
            QuantaRay().close_connection()

        field = '{}-osc_power'.format(self.__class__.__name__)
        data = np.array([(osc_power,)], dtype=[(field, 'float')])
        return data            

    def cleanup(self, abort=False):
        """Turn off the laser.

        :param abort: flag indicating if the experiment is being aborted
        :type abort: bool
        """

        QuantaRay().open_connection()
        QuantaRay().single_shot()
        sleep(1)

        if self._config['watchdog_time'] > 0.0:
            print("...QuantaRay INDI Laser Shutting Down...")
            QuantaRay().turn_off()

        QuantaRay().close_connection()

    def _start_laser(self):
        """
        Start the laser
        """

        #Check if laser is on before turning on
        if 'Oscillator simmer is on' not in str(QuantaRay().get_status()):
            QuantaRay().turn_on()
            print('...waiting 20 seconds for laser to turn on...')
            sleep(20)

        QuantaRay().single_shot()
        QuantaRay().normal_mode()
        QuantaRay().set_osc_power(self._config['start_power_percentage'])
        QuantaRay().set_watchdog(self._config['watchdog_time'])

        if not self._config['specify_shots']:
            QuantaRay().repeat_mode(self._config['watchdog_time'])


    def _control_shots(self, number_of_shots, shot_interval):
        """
        Control the shots from the laser. This is designed to
        run in a separate thread so that it does not block PLACE.
        """

        sleep(5)

        # If the shot interval is the native rep rate (0.1 s),
        # set to REP for the required time to avoid missing shots.
        # Otherwise, fire a single shot at the right interval.
        if shot_interval == 0.1:
            total_time = shot_interval * (number_of_shots - 1)
            QuantaRay().set_watchdog(min(109, 2 * total_time))
            QuantaRay().set('REP')
            sleep(total_time + 0.2)
            QuantaRay().set('SING')
            QuantaRay().set_watchdog(self._config['watchdog_time'])
        else:
            num_shots = 0
            while num_shots < number_of_shots:
                QuantaRay().set(cmd='FIR')
                num_shots += 1

                if num_shots < number_of_shots:
                    sleep(max(0.1, shot_interval))

        sys.exit()

