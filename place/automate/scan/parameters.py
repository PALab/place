"""A class to handle all scan parameters"""
from warnings import warn

class Parameters:
    """A class to handle all scan parameters"""
    def __init__(self):
        # pylint: disable=invalid-name
        self.GROUP_NAME_1 = 'LONG_STAGE',
        self.GROUP_NAME_2 = 'SHORT_STAGE',
        self.MIRROR_DISTANCE = 50,
        self.SCAN = 'point',
        self.SAMPLE_RATE = 'SAMPLE_RATE_10MSPS',
        self.DURATION = 256.0,
        self.CHANNEL = 'CHANNEL_A',
        self.CHANNEL2 = 'null',
        self.AVERAGES = 64,
        self.WAITTIME = 0.0,
        self.RECEIVER = 'none',
        self.RECEIVER2 = 'none',
        self.RETURN = 'True',
        self.SIGNAL_LEVEL = 0.90,
        self.VIB_CHANNEL = 'null',
        self.TRIG_LEVEL = 1.0,
        self.TRIG_RANGE = 4.0,
        self.CHANNEL_RANGE = 'INPUT_RANGE_PM_2_V',
        self.CHANNEL_RANGE2 = 'INPUT_RANGE_PM_2_V',
        self.AC_COUPLING = False,
        self.AC_COUPLING2 = False,
        self.IMPEDANCE = 50,
        self.IMPEDANCE2 = 50,
        self.I1 = 0.0,
        self.D1 = 1.0,
        self.F1 = 0.0,
        self.I2 = 0.0,
        self.D2 = 1.0,
        self.F2 = 0.0,
        self.FILENAME = 'TestScan.h5',
        self.FILENAME2 = 'TestScan.h5',
        self.DECODER = 'DD-300',
        self.DECODER_RANGE = '5mm',
        self.MAP = 'gray',
        self.ENERGY = '0 %',
        self.WAVELENGTH = 1064,
        self.REP_RATE = 10.0,
        self.COMMENTS = '',
        self.PORT_POLYTEC = '/dev/ttyS0',
        self.BAUD_POLYTEC = 115200,
        self.SOURCE = 'none',
        self.PX = 0,
        self.PY = 0,
        self.PLOT = True
        self.DIMENSIONS = None
        self.XPS_1 = None
        self.SOCKET_ID_1 = None
        self.XPS_2 = None
        self.SOCKET_ID_2 = None

    def __getitem__(self, key):
        warn("Dictionary parameters are depricated. Use self.{} instead.".format(key))
        return getattr(self, key)

    def __setitem__(self, key, value):
        if not hasattr(self, key):
            raise AttributeError("{} is not a valid parameter".format(key))
        warn("Dictionary parameters are depricated. Use self.{} instead.".format(key))
        return setattr(self, key, value)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False
