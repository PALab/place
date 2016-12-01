from . import new_focus
from . import polytec
from . import tektronix
from . import xps_control
from . import SRS
from . import quanta_ray
#import scan
#import osci_card   #NOTE: to use the osci_card module to drive an Alazar Tech oscilloscope card, this line must be uncommented.  
                    # The module requires a C library from Alazar to use

__all__ = [
        'new_focus', 'polytec', 'tektronix', 'xps_control',
        'SRS', 'quanta_ray'
        ]

