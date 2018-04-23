import time

from common.audio import *

import numpy as np
from scipy.signal import butter, lfilter

def stft_mag(x, win_len, hop_size, zero_pad_f = 1) :
    """
    Returns spectrogram (magnitude of a STFT) of a signal x. 
    """
    return abs(stft(x, win_len, hop_size, zero_pad_f))

def auto_correlate(x):
    ac = np.correlate(x, x, mode='full')
    return ac[len(x)-1:]

def freqs_of_fft(sample_rate, win_len):
    """
    Get constituent frequencies of a DFT based on
    sample rate of original audio (sample_rate) and window length of 
    the DFT (win_len). 

    Similar to np.fft.fftfreq but takes into account sample rate of audio.
    """
    return np.linspace(0, sample_rate/2., (win_len//2) + 1, endpoint=True)

def stft(x, win_len, hop_size, zp_factor = 1, window = None, centered=True) :
    """
    Return the Short-Time-Fourier-Transform of a signal x. 
    Modified from code written by Eran Egozy under MIT License for 21M.387.

    Inputs:
    x: real-valued signal. 
    win_len: the size of the window.
    hop_size: the hop size (H) for the stft
    zp_factor: zero-pad factor. win_len * zp_factor = fft_len
    window: if None, use Hann window, else, use this as the window

    Outputs:
    Return a matrix of shape [num_bins, num_hops]
    where num_bins = win_len /2 + 1 and num_hops is the total # of hops that "fit" into x.

    """

    if window is None:
        window = np.hanning(win_len)
    else:
        win_len = len(window)

    # zero-pad beginning of x to make centered windows:
    if centered:
        x = np.concatenate((np.zeros(win_len/2), x))

    num_hops = int((len(x) - win_len) / hop_size) + 1
    num_bins = (zp_factor * win_len) / 2 + 1

    output = np.empty((num_bins, num_hops), dtype = np.complex)

    for h in range(num_hops):
        start = h * hop_size
        end = start + win_len
        sig = x[start:end] * window

        # zero pad 
        if zp_factor > 1:
            sig = np.pad(sig, (0, win_len * (zp_factor - 1)), 'constant')

        # take real FFT
        output[: , h] = np.fft.rfft(sig)

    return output


def parabolic_interp(f, x):
    """
    Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    REFACTORED FROM https://gist.github.com/endolith/255291#L38 AS AN 
    IMPLEMENTATION OF PARABOLIC INTERPOLATION. 

    f is a vector and x is an index for that vector.

    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.

    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.

    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def find_peaks(x, win_len=5, thresh=0.9):
    """find highest peak within a neighborhood of win_len. Reject peaks smaller than
    largest peak * thresh
    """
    peaks = []
    hw = win_len / 2
    x_len = len(x)
    x = np.pad(x, hw, mode='edge')
    
    for n in np.arange(x_len):
        win = x[n:n+win_len]
        is_bigger = win < x[n+hw]
        is_bigger[hw] = True     # don't consider the point itself.
        if is_bigger.all():
            peaks.append(n)
    peaks = np.array(peaks)
    
    if len(peaks):

        # find a threshold relative to the highest peak
        th = np.max(x[peaks]) * thresh
        # filter out values that are below th
        peaks = peaks[x[peaks] > th]

    return peaks

def butter_bandpass_filter(signal, lowcut, highcut, fs, order=5):
    """
    Butterworth bandpass filter on signal.
    Inputs:
    signal: signal to filter
    lowcut: lower cutoff frequency 
    highcut: upper cutoff frequency
    fs: sample rate of signal
    order: order of Butterworth filter; default is 5. 
    """
    nyq_frequency = float(fs)/2.
    lowcut, highcut = float(lowcut), float(highcut)
    low_freq, high_freq = lowcut/nyq_frequency, highcut/nyq_frequency
    b, a = butter(order, [low_freq, high_freq], btype='band')
    y = lfilter(b, a, signal)
    return y


def play_signal(x):
    audio = Audio(1)
    x_quieter = x.astype('float') / np.max(x)

    class SignalGenerator(object):
        def __init__(self):
            super(SignalGenerator, self).__init__()
            self.t = 0
        
        def generate(self, num_frames, num_channels):
            assert num_channels == 1
            output = x_quieter[self.t:self.t+num_frames]
            #print output
            self.t += num_frames
            shortfall = num_frames - len(output)
            if shortfall > 0:
                output = np.append(output, np.zeros(shortfall))
            return (output, shortfall == 0)

    audio.set_generator(SignalGenerator())

    while True:
        audio.on_update()
        time.sleep(0.01)
