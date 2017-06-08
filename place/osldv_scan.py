"""OSLDV scan"""
import numpy as np
from numpy.lib import recfunctions as rfn
from obspy.signal.filter import lowpass
from .basic_scan import BasicScan

class OSLDVscan(BasicScan):
    """OSLDV scan class

    Most methods for this scan are the same as those in the BasicScan base
    class. Only the update_phase() method is overridden.
    """
    def update_phase(self):
        """Perform all the updates on the instruments.

        The update phase occurs N times, based on the user configuration for the
        scan. This function loops over the instruments (based on their priority)
        and calls their update method.

        On the first update, PLACE will retrieve the receive the first set of
        data from all the instruments. Based on this data, it will construct
        the record array to be used for the rest of the scan. On each of the
        following updates, PLACE will simply record the data returned from each
        instrument.
        """
        scan_data = None
        for update_number in range(self.config['updates']):
            current_data = np.array([(update_number,)], dtype=[('update', 'int16')])
            for instrument in self.instruments:
                print("...{}: updating {}...".format(update_number,
                                                     instrument.__class__.__name__))
                instrument_data = instrument.update(update_number, self.socket)
                postfix_string = '-' + instrument.__class__.__name__
                if instrument_data is not None:
                    current_data = rfn.join_by('update',
                                               current_data,
                                               instrument_data,
                                               jointype='leftouter',
                                               r2postfix=postfix_string,
                                               usemask=False,
                                               asrecarray=False)
            postprocessed_data = self.osldv_postprocessing(current_data)
            if update_number == 0:
                scan_data = postprocessed_data.copy()
                scan_data.resize(self.config['updates'])
            else:
                scan_data[update_number] = postprocessed_data[0]

        with open(self.config['directory'] + '/scan_data.npy', 'xb') as data_file:
            np.save(data_file, scan_data)

    def osldv_postprocessing(self, data):
        """Performs postprocessing on the data returned from the ATS card."""
        sample_rate = self.metadata['sampling_rate']
        delta = 1 / sample_rate
        t = np.arange(0, len(data)*delta, delta)
        trace_data = data['trace'][0]
        data = rfn.drop_fields(data, 'trace', usemask=False)
        channel = 0
        new_data = [lowpass_filter(record, sample_rate, t) for record in trace_data[channel]]
        return rfn.append_fields(data, 
                                 'trace',
                                 new_data.mean(axis=0, dtype='float64'),
                                 usemask=False)

def lowpass_filter(record, sample_rate, t):
    """Apply the lowpass filter to the data."""
    fc = 40e6
    #### Compute I and Q from raw data
    Q = lowpass((np.cos(2*np.pi*fc*t)*record), fc, sample_rate, corners=4)
    I = lowpass((np.sin(2*np.pi*fc*t)*record), fc, sample_rate, corners=4)        
    print(str(Q))
    print(str(I))
    return np.array(
        (I[1:]*np.diff(Q)/np.diff(t) - Q[1:]*np.diff(I)/np.diff(t))
        / ((I[1:]**2 + Q[1:]**2))) / (2*np.pi)
