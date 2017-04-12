'''
Created on Jul 6, 2013

@author: henrik
'''
#pylint: disable=invalid-name
from struct import unpack
from functools import reduce
from place.alazartech import atsapi as ats

def getNamesOfConstantsThatStartWith(beginning):
    ''' Returns all constants defined in AlazarCmd that start with beginning. '''
    return [c for c in dir(ats) if c[:len(beginning)] == beginning]

def getValueOfConstantWithName(name):
    """returns the value of the constants defined in AlazarCmd that is called name. """
    return getattr(ats, name)

def getValuesOfConstantsThatStartWith(beginning):
    """returns all values of constants defined in AlazarCmd that start with beginning. """
    return [eval("ats." + c) for c in dir(ats) if c[:len(beginning)] == beginning]

def getSampleRateFrom(name):
    """converts a string defining a sample rate to the rate in Hertz."""
    name = name.lstrip("SAMPLE_RATE_")
    name = name.rstrip("SPS")
    if name[-1] == "K":
        exponent = 3
        name = name.rstrip("K")
    elif name[-1] == "M":
        exponent = 6
        name = name.rstrip("M")
    elif name[-1] == "G":
        exponent = 9
        name = name.rstrip("G")
    return int(name) * 10 ** exponent

def getInputRangeFrom(name):
    """converts a string defining a input range to the range in Volt."""
    name = name.lstrip("INPUT_RANGE_PM_")
    name = name.rstrip("V")
    exponent = 0
    if name[-1] == "M":
        exponent = -3
        name = name.rstrip("M")
    name = name.rstrip('_')
    return int(name) * 10 ** exponent

# Author: A.Polino
def is_power2(num):
    ''' states if a number is a power of two '''
    return num != 0 and ((num & (num - 1)) == 0)

# Author: unknown
def factors(num):
    ''' return a set of factors '''
    return set(reduce(list.__add__, \
                      ([i, num // i] for i in range(1, int(num ** 0.5) + 1) if num % i == 0)))

def getBiggestFactor(num):
    ''' no docstring '''
    if num == 0:
        return 0
    elif num == 1:
        return 1
    facs = factors(num)
    facs.discard(max(facs))
    return max(facs)

def convert_raw_data_to_ints(raw):
    '''
    converts the data that is saved byte wise in little endian order
    to integers.
    '''
    a_value = len(raw)
    shorts = unpack(str(a_value) + 'B', raw)
    a_value = len(shorts)
    return [(shorts[2 * i + 1] * 256 + shorts[2 * i]) // 4 for i in range(a_value // 2)]
