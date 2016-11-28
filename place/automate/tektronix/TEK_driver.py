'''
Module to communicate with Tektronix TDS3014b oscilloscope using ethernet.

See example_tektronix.py for example usage.

Modified from module developed by Joe Gregorio, (C) 2006 MIT:
ftp://sprite.ssl.berkeley.edu/pub/sharris/MAVEN_LPW_Preamp/109_TDS3014B_control/tds3014b.py

@author: Jami L Johnson
Created May 27, 2014
'''
from __future__ import print_function, absolute_import

from . import httplib2
import urllib
import os
import struct
import datetime
from obspy import read, Trace, UTCDateTime
from obspy.core.trace import Stats

try:
    import numpy as np

except ImportError:
    pass

class Error(Exception): pass
class connection_error(Error): pass

class TDS3014b:
    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.base_url = "http://%s" % (ip_addr)
        self.h = httplib2.Http()

    def gpibCMD(self, cmd):
        """
        Send a command to the scope and gets the response, if any.
        """
        if(cmd.startswith('*')):
            prefix = ''
        else:
            prefix = ':'

        cmd_url = "?COMMAND=%s%s" % (prefix, urllib.quote_plus(cmd))
        url = '/'.join([self.base_url, cmd_url])
        f = urllib.urlopen(url)
        content = f.read()
        f.close()
        return content

    def getScreen(self):
        """
        :returns: a screen shot in PNG format.
        """
        url = '/'.join([self.base_url, 'Image.png'])
        try:
            f = urllib.urlopen(url)
        except IOError as e:
            raise connection_error(e)
        content = f.read()
        f.close()

        return content

    def forceTrigger(self):
        """
        Forces scope to trigger
        """
        self.gpibCMD('FPANEL:PRESS FORCETRIG')

    def parseISF(self, isf_data, header_only=None, convert=None):
        """
        Determine starting point of data.
        Header has something like 'CURVE #520000', where ascii '5' is the
        length of the length field '20000'.

        ::

            'CURVE #520000xxxx...'
              ^      ^^    ^
              |      ||    +---- data_loc:    location of first valid byte of data
              |      |+--------- len_loc:     location of first byte of data length field
              |      +---------- len_len_loc: location of length of length
              +----------------- tag_loc:     location of start tag
        """
        start_tag = 'CURVE #'
        tag_loc = int(isf_data.find(start_tag))
        len_len_loc = tag_loc + len(start_tag)
        len_loc = len_len_loc + 1
        len_len = int(isf_data[len_len_loc]) # e.g. 5
        data_loc = len_loc + len_len
        data_len = int(isf_data[len_loc:len_loc+len_len]) # e.g. 20000

        # Extract and parse header
        header = isf_data[:tag_loc]
        # Reformat the header into a dictionary
        header_dict = {}
        items = header.replace(':WFMPRE:','').replace(':','').split(';') # list of "key value" pairs
        for item in items:
            if(item):
                key, value = item.split(' ', 1) # maxsplit 1 to ignore subsequent spaces in value
                value = value.replace('"', '')
                header_dict[key] = value

        if(header_only):
            return header_dict

        # Extract data and convert from string to integer value
        data = isf_data[data_loc:]

        stats = Stats()
        stats.npts = int(header_dict['NR_PT'])
        stats.calib = float(header_dict['YMULT'])
        byte_order = header_dict['BYT_OR'] # 'MSB' or 'LSB'

        if(byte_order == 'MSB'):
            byte_order = '>'
        else:
            byte_order = '<'
        points = []
        for i in range(0, stats.npts*2, 2):
            value = data[i:i+2] # as string
            converted = struct.unpack('%sh' % byte_order, value)[0]
            points.append(converted)

        # Optionally convert points to engineering units
        if(convert):
            try:
                points = np.array(points) * stats.calib  # requires numpy
            except NameError:
                # If numpy not available, use list instead.
                p = []
                for point in points:
                    p.append(point * stats.calib)
                points = p
        stats.time_offset = float(header_dict['XZERO'])
        stats.calib_unit = header_dict['YUNIT']
        stats.delta = float(header_dict['XINCR'])
        stats.amp_offset = float(header_dict['YOFF'])
        stats.comments = header_dict['WFID']
        stats.channel = header_dict['WFID'][0:3]

        return stats, points

    def getWaveform(self, channel=1, format=None):
        """
        Returns the data points that make up the currently displayed
        waveform. There will be 10,000 points spanning the X-axis time,
        and 7 bits spanning the Y-axis voltage. The time and voltage
        range depend on how the scope is currently configured, and this
        configuration is returned as metadata depending on the value of
        format.

        Arguments:

        :param channel: Integer, 1-4
        :param format: String (see below).
        :returns: Data representing the currently displayed waveform
                  from the oscilloscope in the format described above.


        format argument

        Optional argument specifying what format the returned data
        should be in. Default value is 'eng'. Possible values and
        their effect on the return value are:

        **raw**
            return value will contain only the raw ISF-formatted
            data from the scope. See notes on ISF below.

        **csv**
            return value is a (header, data) tuple, where header is a
            python dict of terms describing the data. Data is a string
            of the 10k data points from the scope in ASCII/CSV format.

            Note that this takes about 20 seconds as opposed to <1
            second for ISF.

        **counts**
            return value is a (header, data) tuple where header is a
            python dictionary of terms describing data, which is a numpy
            array of data points in ADC counts. (If numpy is installed,
            otherwise data is a list.) The header information can be
            used to convert counts to volts.

        **eng**
            return value is a (header, data) tuple as in the 'array'
            case above, only the header will be examined in order to
            return the data points in volts (as floating point numbers).


        Exceptions:

        E.g.:

        getWaveform(channel=1)

        Notes:

        For 'eng' and 'array' formats, the TDS3014B generates 9-bit
        samples, which are packed into a two-byte signed integer. For
        example, 0xF300 = -3328 -3328 * YMULT of 1.5625e-4 = -0.52 volts

        See also:

        http://www.photonics.umd.edu/software/isfread.m
            Example ISF decoder using matlab.

        http://www2.tek.com/cmswpt/swdetails.lotr?ct=SW&cs=sut&ci=5355&lc=EN
            ISF to CSV Conversion utility from Tektronix (DOS)

        http://www.tek.com/forum/viewtopic.php?f=5&t=50
            Notes on ISF header format.
        """

        if(format == None):
            format = 'eng' # Default format

        # get data in ISF format first. If the user requested CSV, return the
        # header from the ISF request along with the CSV data from a second
        # request. This keeps the return value format similar for both cases and
        # ensures that the user doesn't just get CSV data with no metadata.
        content = self.fetchData(channel, format='internal')

        if(format == 'raw'):
            return content
        elif(format == 'csv'):
            header = self.parseISF(content, header_only=True)
            csv_data = self.fetchData(channel, format='spreadsheet')
            return header, csv_data
        elif(format == 'counts'):
            header, points = self.parseISF(content, convert=False)
            return header, points
        elif(format == 'eng'):
            header, points = self.parseISF(content, convert=True)

            return header, points

    def fetchData(self, channel, format):
        """
        Get readout of current data.
        Communicate with the scope and request a readout of the current
        data. Format can be either 'internal' (for ISF data) or
        'spreadsheet' (for CSV).
        """
        data = urllib.urlencode([('command', 'select:ch%d on' % (channel)),
                                 ('command', 'save:waveform:fileformat %s' % (format)),
                                 ('wfmsend', 'Get')])
        url = '/'.join([self.base_url, "getwfm.isf"])
        response, content = self.h.request(url, "POST", data)
        content = content[:-3] # remove '\n\r\n' from content
        return content

    def getIDN(self):
        return self.gpibCMD('*IDN?')

    def getMeasurement(self, meas_num, numeric=False):
        """
        Queries the scope for the measurement number meas_num.  The
        scope can have up to four measurements which are user
        configured.

        e.g.:
        >>> result = t.get_measurement(1) # Get measurement for MEAS1
        >>> print result
        '1.3312E-8'

        The units for the measurement can be determined by using
        get_measurement_params() (below).

        """
        if(1 <= meas_num <= 4):
            retval = self.gpibCMD('measurement:MEAS%d:data?' % meas_num).strip().split(',')[0]
            if(numeric):
                retval = float(retval)
            return retval
        else:
            msg = "ERROR: meas_num must be between 1 and 4 inclusive."
            print(msg)
            raise Error(msg)

    def getMeasurementParams(self, meas_num):
        """
        Queries the scope for the parameters for measurement number
        meas_num.  Returns a string.

        e.g.:
        >>> result = t.getMeasurementParams(3) # get parameters for MEAS3
        >>> print result
        'FREQ;"Hz";CH1;CH2;FORW;RIS;RIS;1'

        """
        if(1 <= meas_num <= 4):
            return self.gpibCMD('measurement:MEAS%d?' % meas_num).strip()
        else:
            msg = "ERROR: meas_num must be between 1 and 4 inclusive."
            print(msg)
            raise Error(msg)

    def recallSavedConfig(self, config_num):
        """
        Recalls scope saved configuration number config_num.
        """
        self.gpibCMD('recall:setup %d' % (config_num))

    def setVscale(self, chan_num, vdiv):
        """
        Sets the vertical scale for the specified channel to the
        specified scale.  Scale is in volts per division.

        e.g.:
        >>> t.setVscale(2, .5) # set ch. 2 to 500 mV/div
        """

        self.gpibCMD('ch%d:scale %s' % (chan_num, vdiv))

    def setHscale(self, secdiv=None, freq=None):
        """
        Sets the scope horizontal timebase.  The scale can either be
        specified by supplying the secdiv parameter, in which case the
        scale is set to the given seconds per division.  Or it can be
        set by supplying a frequency.  The seconds per division value
        will be calculated such that 10 cycles of the given frequency
        will be shown on screen.

        e.g.:
        >>> t.setHscale(secdiv=1) # 1 second per division
        >>> t.setHscale(freq=100) # 10 ms/div
        """
        if(secdiv != None):
            self.gpibCMD('horizontal:main:scale %s' % (str(secdiv)))
        elif(freq != None):
            secdiv = 1.0/freq
            self.gpibCMD('horizontal:main:scale %s' % (str(secdiv)))
        else:
            msg = "ERROR: One of secdiv or freq must be specified."
            print(msg)
            raise Error(msg)

def test():
    scope = TDS3014B('localhost:31338')
    return scope


