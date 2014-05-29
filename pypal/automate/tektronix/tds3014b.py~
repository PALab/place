"""
tds3014b.py - Script to provide control and data acquisition from the
Tektronix TDS3014B oscilloscope via Ethernet.

Example Usage:
>>> import tds3014b
>>> t = tds3014b.tds3014b(ip_addr='192.168.0.106')

Send a GPIB command to the scope - the return value is the response from the scope.
>>> t.gpib_cmd('*IDN?')
'TEKTRONIX,TDS 3014B,0,CF:91.1CT FV:v3.27 TDS3GV:v1.00 TDS3FFT:v1.00 TDS3TRG:v1.00\n'

>>> t.beep() # Make a sound

Fetch the current scope screen as an image:
>>> screen = t.get_screen() # PNG image data in a variable
>>> screen = t.get_screen('tds_screen.png') # PNG data in var and written to disk

Fetch the current data for a waveform on the specified channel using
get_waveform.  get_waveform returns a header, containing metadata
about the waveform, and the data as a list of points.

>>> header, data = t.get_waveform(channel=1, format='eng') # returns header (dict) and converted data points (array)
>>> header, data = t.get_waveform(channel=1, format='counts') # same as above but data points are in ADC counts instead of volts
>>> header, data = t.get_waveform(channel=1, format='csv') # data format is csv string
>>> header, data = t.get_waveform(channel=1, plot=True) # Will display plot on screen

The data can also be plotted afterwards using plot():
>>> t.plot(header, data)

Requirements:
For plotting, Numpy and Matplotlib are required. If you do not intend to plot,
only Python is required.
"""
import httplib2 # for Http
import urllib # for urlencode
import os
import struct
import datetime

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg') # Set backend to Agg instead of Tk.  This allows rendering instead of a GUI.
    import matplotlib.pyplot as plt
except ImportError:
    pass

class Error(Exception): pass
class connection_error(Error): pass

class tds3014b:
    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.base_url = "http://%s" % (ip_addr)
        self.h = httplib2.Http()

    def beep(self):
        self.gpib_cmd('BELL')
        
    def gpib_cmd(self, cmd):
        """
        Send a command to the scope and gets the response, if any.
        Commands are anything from the programming menu that you would
        typically send over GPIB, such as 'BUSY?' or 'FPANEL:PRESS
        clearmenu'.  The commands are sent by encoding them into a URL
        like this: http://192.168.0.106/?COMMAND=:BUSY?
        """
        # Commands that start with '*' (like *IDN?) shouldn't get a
        # ':' prefix.  Not exactly sure what the spec is, but this
        # works.
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

    def get_screen(self, filename=None, show=False):
        """
        Returns the current on-screen image in PNG format as a string
        of bytes.  If a filename is supplied, writes the PNG data to
        disk instead of returning it. If show=True, brings up the image in a web
        browser instead of returning it.
        """
        url = '/'.join([self.base_url, 'Image.png'])
        try:
            f = urllib.urlopen(url)
        except IOError, e:
            raise connection_error(e)
        content = f.read()
        f.close()

        if(not (filename or show)):
            return content

        if(filename):
            f = open(filename, 'wb')
            f.write(content)
            f.close()

        if(show):
            if(filename):
                pass
            else:
                # Assign a temporary filename and write out the file
                filename = 'scope_screen_tmp.png'
                f = open(filename, 'wb')
                f.write(content)
                f.close()
            import webbrowser
            webbrowser.open(filename)

    
    def force_trig(self):
        """ If the scope is in a state where the force trig button
        would trigger it, this would do the same thing.
        """
        self.gpib_cmd('FPANEL:PRESS FORCETRIG')

    def parse_isf(self, isf_data, header_only=None, convert=None):
        """
        """
        # Figure out where start of data is.
        # Header has something like 'CURVE #520000', where ascii '5' is the
        # length of the length field '20000'.
        # 'CURVE #520000xxxx...'
        #  ^      ^^    ^
        #  |      ||    +---- data_loc:    location of first valid byte of data
        #  |      |+--------- len_loc:     location of first byte of data length field
        #  |      +---------- len_len_loc: location of length of length
        #  +----------------- tag_loc:     location of start tag
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

        num_pts = int(header_dict['NR_PT'])
        byte_order = header_dict['BYT_OR'] # 'MSB' or 'LSB'
        if(byte_order == 'MSB'):
            byte_order = '>'
        else:
            byte_order = '<'
        points = []
        for i in range(0, num_pts*2, 2):
            value = data[i:i+2] # as string
            converted = struct.unpack('%sh' % byte_order, value)[0]
            points.append(converted)
            #print i, repr(value), '-->', converted

        # Optionally onvert points to engineering units
        if(convert):
            ymult = float(header_dict['YMULT'])
            try:
                points = np.array(points) * ymult  # requires numpy
            except NameError:
                # If numpy not available, use list instead.
                p = []
                for point in points:
                    p.append(point * ymult)
                points = p

        return header_dict, points

    def get_waveform(self, channel=1, format=None, plot=None):
        """
        Returns the data points that make up the currently displayed
        waveform. There will be 10,000 points spanning the X-axis time, and 7
        bits spanning the Y-axis voltage. The time and voltage range depend on
        how the scope is currently configured, and this configuration is
        returned as metadata depending on the value of format.

        Arguments:
         channel: Integer, 1-4
         format : String.  Optional argument specifying what format the
                  returned data should be in. Default value is 'eng'. Possible
                  values and their effect on the return value are:

                  'raw': return value will contain only the raw ISF-formatted
                  data from the scope. See notes on ISF below.
                  
                  'csv': return value is a (header, data) tuple, where header is
                  a python dict of terms describing the data. Data is a string
                  of the 10k data points from the scope in ASCII/CSV format.
                  Note that this takes about 20 seconds as opposed to <1 second
                  for ISF.
                  
                  'counts': return value is a (header, data) tuple where header
                  is a python dictionary of terms describing data, which is a
                  numpy array of data points in ADC counts. (If numpy is installed, otherwise data is a
                  list.) The header information can be used to convert counts to
                  volts.
                  
                  'eng': return value is a (header, data) tuple as in the
                  'array' case above, only the header will be examined in order
                  to return the data points in volts (as floating point
                  numbers).

         plot:    Bool.  If true, a plot of the data will be written to disk
                  be displayed on screen. Only valid for 'counts' and 'eng'
                  formats.

        Returns:
         Data representing the currently displayed waveform from the
         oscilloscope in the format described above.

        Exceptions:
        
        E.g.:
         get_waveform(channel=1)

        Notes:

        For 'eng' and 'array' formats, the TDS3014B generates 9-bit samples,
        which are packed into a two-byte signed integer. For example, 0xF300 =
        -3328 -3328 * YMULT of 1.5625e-4 = -0.52 volts
        
        See also: 
         http://www.photonics.umd.edu/software/isfread.m
          Example ISF decoder using matlab.

         http://www2.tek.com/cmswpt/swdetails.lotr?ct=SW&cs=sut&ci=5355&lc=EN
          ISF to CSV Conversion utility from Tektronix (DOS)
        
         http://www.tek.com/forum/viewtopic.php?f=5&t=50
          Notes on ISF header format.          
        """
        # The scope really only understand these two formats (csv and ISF). For
        # 'eng', the code below applies a conversion formula.
        if(format == None):
            format = 'eng' # Default value for format

        # get data in ISF format first. If the user requested CSV, return the
        # header from the ISF request along with the CSV data from a second
        # request. This keeps the return value format similar for both cases and
        # ensures that the user doesn't just get CSV data with no metadata.
        content = self.fetch_data(channel, format='internal')

        if(format == 'raw'):
            return content
        elif(format == 'csv'):
            # parse header
            header = self.parse_isf(content, header_only=True)
            # Get CSV data
            csv_data = self.fetch_data(channel, format='spreadsheet')
            return header, csv_data
        elif(format == 'counts'):
            header, points = self.parse_isf(content, convert=False)
            if(plot):
                self.plot(header, points)
            return header, points
        elif(format == 'eng'):
            header, points = self.parse_isf(content, convert=True)
            if(plot):
                self.plot(header, points)
            return header, points
    
    def fetch_data(self, channel, format):
        """
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

    def plot(self, header, data, xlabel='', ylabel='', title='', show=True, filename=None):
        """
        Write data to disk as png file and display it in a webbrowser.
        """
        # The main disadvantage to doing this (writing to disk instead of using
        # the Tk GUI) is that you can't zoom in or do anything interactive with
        # the data.

        chan_str = header['WFID'].split(',')[0].lower()
        time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        title = header['WFID']
        xlabel = header['XUNIT']
        ylabel = header['YUNIT']
        xzero = float(header['XZERO'])
        xincr = float(header['XINCR'])
        xend = xzero + (len(data) * xincr)
        x_data = np.arange(xzero, xend, xincr)

        plt.plot(x_data, data)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.title(title)
        plt.axis('tight')

        if(not filename):
            filename = '%s_%s.png' % (time_str, chan_str)
        plt.savefig(filename)

        if(show):
            import webbrowser
            webbrowser.open(filename)
        plt.clf()

    def get_idn(self):
        return self.gpib_cmd('*IDN?')

    def get_measurement(self, meas_num, numeric=False):
        """
        Queries the scope for the measurement number meas_num.  The scope can
        have up to four measurements which are user configured.

        e.g.:
        >>> result = t.get_measurement(1) # Get measurement for MEAS1
        >>> print result
        '1.3312E-8'

        The units for the measurement can be determined by using
        get_measurement_params() (below).
        
        """
        if(1 <= meas_num <= 4):
            retval = self.gpib_cmd('measurement:MEAS%d:data?' % meas_num).strip().split(',')[0]
            if(numeric):
                retval = float(retval)
            return retval
        else:
            msg = "ERROR: meas_num must be between 1 and 4 inclusive."
            print msg
            raise Error(msg)

    def get_measurement_params(self, meas_num):
        """
        Queries the scope for the parameters for measurement number
        meas_num.  Returns a string.

        e.g.:
        >>> result = t.get_measurement_params(3) # get parameters for MEAS3
        >>> print result
        'FREQ;"Hz";CH1;CH2;FORW;RIS;RIS;1'
        
        """
        if(1 <= meas_num <= 4):
            return self.gpib_cmd('measurement:MEAS%d?' % meas_num).strip()
        else:
            msg = "ERROR: meas_num must be between 1 and 4 inclusive."
            print msg
            raise Error(msg)

    def recall_saved_config(self, config_num):
        """
        Recalls scope saved configuration number config_num.
        """
        #print >> log, "Recalling scope saved config %d" % (config_num)
        self.gpib_cmd('recall:setup %d' % (config_num))

    def set_vscale(self, chan_num, vdiv):
        """

        Sets the vertical scale for the specified channel to the
        specified scale.  Scale is in volts per division.

        e.g.:
        >>> t.set_vscale(2, .5) # set ch. 2 to 500 mV/div
        """

        self.gpib_cmd('ch%d:scale %s' % (chan_num, vdiv))

    def set_hscale(self, secdiv=None, freq=None):
        """

        Sets the scope horizontal timebase.  The scale can either be
        specified by supplying the secdiv parameter, in which case the
        scale is set to the given seconds per division.  Or it can be
        set by supplying a frequency.  The seconds per division value
        will be calculated such that 10 cycles of the given frequency
        will be shown on screen.

        e.g.:
        >>> t.set_hscale(secdiv=1) # 1 second per division
        >>> t.set_hscale(freq=100) # 10 ms/div

        """
        if(secdiv != None):
            self.gpib_cmd('horizontal:main:scale %s' % (str(secdiv)))
        elif(freq != None):
            secdiv = 1.0/freq
            self.gpib_cmd('horizontal:main:scale %s' % (str(secdiv)))
        else:
            msg = "ERROR: One of secdiv or freq must be specified."
            print msg
            raise Error(msg)
        

    
def test():
    #t = tds3014b('192.168.0.106')
    t = tds3014b('localhost:31338')
    return t

