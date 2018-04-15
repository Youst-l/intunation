import numpy as np

def stft_mag(x, win_len, hop_size, zero_pad_f = 1) :
    """
    Returns spectrogram (magnitude of a STFT) of a signal x. 
    """
    return abs(stft(x, win_len, hop_size, zero_pad_f))


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
