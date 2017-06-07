"""OSLDV scan"""
import numpy as np
from numpy.lib import recfunctions as rfn
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
        # create the column for the update (step) number
        data = np.recarray((1,), dtype=[('update', int)])
        data[0] = (0,)

        for update_number in range(self.config['updates']):
            if update_number == 0:
                for instrument in self.instruments:
                    print("...{}: updating {}...".format(update_number,
                                                         instrument.__class__.__name__))
                    new_data = instrument.update(update_number, self.socket)
                    if new_data is not None:
                        # postprocess the trace before putting data in record array
                        if instrument.__class__.__name__[0:3] == 'ATS':
                            new_data = osldv_postprocessing(new_data)
                        data = rfn.rec_append_fields(
                            data,
                            new_data.dtype.names,
                            [new_data[col] for col in new_data.dtype.names],
                            dtypes=[new_data.dtype[i] for i in range(len(new_data.dtype))])
                data = data.copy()
                data.resize((self.config['updates'],))
            else:
                for instrument in self.instruments:
                    print("...{}: updating {}...".format(update_number,
                                                         instrument.__class__.__name__))
                    new_data = instrument.update(update_number, self.socket)
                    if new_data is not None:
                        # postprocess the trace before putting data in record array
                        if instrument.__class__.__name__[0:3] == 'ATS':
                            new_data = osldv_postprocessing(new_data)
                        for name in new_data.dtype.names:
                            data[update_number][name] = new_data[name]
        with open(self.config['directory'] + '/data.npy', 'xb') as data_file:
            np.save(data_file, data)

def osldv_postprocessing(data):
    """Performs postprocessing on the data returned from the ATS card."""
    return data
