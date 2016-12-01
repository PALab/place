'''
Created on Jul 6, 2013

@author: henrik
'''
try:
    import AlazarCmd as cons
except ImportError:
    pass # methods to this module will fail
from functools import reduce

def getNamesOfConstantsThatStartWith(beginning):
    """returns all constants defined in AlazarCmd that start with beginning. """
    return [c for c in dir(cons) if c[:len(beginning)] == beginning]

def getValueOfConstantWithName(name):
    """returns the value of the constants defined in AlazarCmd that is called name. """
    return eval("cons." + name)

def getValuesOfConstantsThatStartWith(beginning):
    """returns all values of constants defined in AlazarCmd that start with beginning. """
    return [eval("cons." + c) for c in dir(cons) if c[:len(beginning)] == beginning]

def getSampleRateFrom(name):
    """converts a string defining a sample rate to the rate in Hertz."""
    import string
    name = string.lstrip(name, "SAMPLE_RATE_")
    name = string.rstrip(name, "SPS")
    if name[-1] == "K":
        exponent = 3
        name = string.rstrip(name, "K")
    elif name[-1] == "M": 
        exponent = 6
        name = string.rstrip(name, "M")
    elif name[-1] == "G": 
        exponent = 9
        name = string.rstrip(name, "G")
    return int(name) * 10 ** exponent

def getInputRangeFrom(name):
    """converts a string defining a input range to the range in Volt."""
    import string
    name = string.lstrip(name, "INPUT_RANGE_PM_")
    name = string.rstrip(name, "V")
    exponent = 0
    if name[-1] == "M":
        exponent = -3
        name = string.rstrip(name, "M")
    name = string.rstrip(name, '_')
    return int(name) * 10 ** exponent

# Author: A.Polino
def is_power2(num):

    'states if a number is a power of two'

    return num != 0 and ((num & (num - 1)) == 0)

# Author: unknown
def factors(n):    
    return set(reduce(list.__add__, \
                      ([i, n // i] for i in range(1, int(n ** 0.5) + 1) if n % i == 0)))

def getBiggestFactor(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    facs = factors(n)
    facs.discard(max(facs))
    return max(facs)
