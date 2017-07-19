"""OSLDV scan"""
import numpy as np
from numpy.lib import recfunctions as rfn
import matplotlib.pyplot as plt
try:
    from obspy.signal.filter import bandpass # pylint: disable=import-error
    from obspy.signal.filter import lowpass # pylint: disable=import-error
except ImportError:
    pass
from scipy.signal import hilbert
from .basic_scan import BasicScan

TWO_PI = 2 * np.pi

class OSLDVscan(BasicScan):
    """OSLDV scan class

    Most methods for this scan are the same as those in the BasicScan base
    class. Only the _postprocessing() method is overridden.
    """
    def _postprocessing(self, data):
        """Performs OSLDV postprocessing on the row data."""
        field = 'trace'
        row = 0
        channel = 0
        records = data[field][row][channel].copy()
        other_data = rfn.drop_fields(data, field, usemask=False)
        sampling_rate = self.metadata['sampling_rate']
        new_records = np.array([lowpass_filter(signal, sampling_rate) for signal in records])
        average_record = np.array((1,), dtype=[('trace', 'float64', len(new_records[0]))])
        average_record['trace'] = new_records.mean(axis=0)
        new_data = rfn.merge_arrays([other_data, average_record], flatten=True, usemask=False)
        #### Plot the average results
        times = np.arange(0, len(average_record['trace'])) * (1e6 / sampling_rate)
        plt.figure('OSLDV postprocessing')
        plt.ion()
        plt.clf()
        plt.plot(times, average_record['trace'])
        plt.xlabel(r'Time [microseconds]')
        plt.ylabel(r'Velocity[m/s]')
        plt.pause(0.05)
        return new_data

def calc_iq(signal, times, sampling_rate):
    """Compute I and Q values."""
    fc_value = 40e6
    cutoff = 5e6
    adjusted_times = TWO_PI * fc_value * times
    signal = bandpass(signal,
                      fc_value - cutoff,
                      fc_value + cutoff,
                      sampling_rate,
                      corners=4,
                      zerophase=True)
    cos_data = np.cos(adjusted_times) * signal
    sin_data = np.sin(adjusted_times) * signal
    q_values = lowpass(cos_data, cutoff, sampling_rate, corners=4, zerophase=True)
    i_values = lowpass(sin_data, cutoff, sampling_rate, corners=4, zerophase=True)
    return i_values, q_values

def frequency(signal, sampling_rate):
    """frequency"""
    quad = hilbert(signal)
    phase = (np.arctan2(np.imag(quad), np.real(quad)))
    freq = np.diff(phase)/(TWO_PI*sampling_rate)
    return freq

def vfm(i_values, q_values, times):
    """Computer VFM"""
    q_part = q_values[1:] * np.diff(i_values) / np.diff(times)
    i_part = i_values[1:] * np.diff(q_values) / np.diff(times)
    q_squared = q_values[1:]**2
    i_squared = i_values[1:]**2
    return np.array((i_part - q_part) / (i_squared + q_squared)) / TWO_PI

def lowpass_filter(signal, sampling_rate):
    """Apply the lowpass filter to the data."""
    wavelength = 632.8e-9
    times = np.arange(0, len(signal)) * (1 / sampling_rate)
    i_values, q_values = calc_iq(signal, times, sampling_rate)
    freq = vfm(i_values, q_values, times)
    return freq * wavelength / 2
