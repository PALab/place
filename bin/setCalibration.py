from place.automate.polytec.vibrometer import PolytecSensorHead, FOCUS_SENSORHEAD_0
from place.automate.scan.scan_functions import initialize
from place.automate.new_focus.Calibrate import getConversion, Position, getInverse


def main():
    # Sets calibration values when the scanning mirror is repositioned.
    # Currently only for use with polytec sensor head.
    [pico_controller, x_mot, y_mot] = initialize().PicomotorController()
    inverse = getInverse()
    print("Position mirror for auto-focus")
    Position(x_mot, y_mot, inverse=inverse)
    PolytecSensorHead().autofocusVibrometer()
    focuslength = float(PolytecSensorHead().get_attr(FOCUS_SENSORHEAD_0))
    getConversion(x_mot, y_mot, focuslength=focuslength, method='manual', inverse=inverse)
    pico_controller.close()
    return

if __name__ == '__main__':
    main()
