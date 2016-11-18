'''
Created on Jul 6, 2013

@author: Henrik tom Woerden
'''
from __future__ import print_function

import re
import ctypes

class ConstantParseError(Exception):
    pass

def parseHeader(header, newHeader):
    """ 
    parse constants of the type "#define constantname value" and creates a new python file that define respective variables as ctypes
    """
    f = open(header, 'r')
    o = open(newHeader, 'w')
    o.write("from ctypes import*\n")
    print("Start to create a python file that allows access to Alazar constants.")
    print("Some constants might not be parsed...")
    for line in f:
        if line != None and _isDefineStatement(line):
            var, val = _extractConstant(line)
            if val != None:
                o.write(var + ' = ' + str(val) + '\n')
    f.close()
    o.close()
    print("Finished parsing constants.")

def _isDefineStatement(s):
    if s.find("#define") == 0:
        return True
    else :
        return False
    
def _extractConstant(s):
    # get rid of the define
    s = s.lstrip("#define ")
    # get rid of comments
    comment = s.find(r"//")
    s = s[:comment]
    # split name from value
    s = s.split()
    # check if parsing is possible
    if len(s) > 2:
        print("unparsed: ", s[0])
        return s[0], None
    if len(s) == 1:
        return s[0], None
    # get rid of numeric suffixes and decide on the ctype
    suffixe = re.findall('[a-wy-zG-WY-Z]', s[1])
    if suffixe != []:
        unsigned = False
        longint = False
        for suffix in suffixe:
            if suffix == 'U':
                unsigned = True
                s[1] = s[1].replace('U', '')
            elif suffix == 'L':
                longint = True
                s[1] = s[1].replace('L', '')
            else:
                print("unparsed: ", s[0])
                return s[0], None
        if unsigned and longint:
            return s[0], ctypes.c_ulong(eval(s[1]))
        if unsigned:
            return s[0], ctypes.c_uint(eval(s[1]))
        if longint:
            return s[0], ctypes.c_long(eval(s[1]))
        raise ConstantParseError("reached end of function without return")
    return s[0], None
