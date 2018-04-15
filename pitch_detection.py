from util import *
from scipy.io import wavfile

def detect_pitch(signal, fs):
    """
    Pitch detection of a signal using parabolic interpolation on the STFT.

    TODO: Implement based on YIN algorithm (combine this w/ autocorrelation):
    https://asa.scitation.org/doi/pdf/10.1121/1.1458024

    Inputs:
    signal: real-valued audio signal assumed to be sampled at 44100 Hz. 
    fs: sample rate of signal 
    """
    # PARAMETERS 
    sample_rate = float(fs)
    freq_min, freq_max = 40, 4000 # frequency range of human voice in Hz 
    win_len = 4096
    hop_size = win_len / 4
    max_thresh = 0.1
    eps = 0.0000001

    # Get spectrogram (magnitude STFT) from audio signal and the constituent freqs
    spec = stft_mag(signal, win_len, hop_size)
    fft_freqs = freqs_of_fft(sample_rate, win_len)

    # Average points and shift, pad to input size, avoid divide by zero errors
    shift_two = spec[2:]-spec[:-2]
    average = shift_two*0.5
    shift = 2*(spec[1:-1] - shift_two)
    shift[shift < eps] = eps
    shift = average / shift
    avg = np.pad(average, ((1, 1), (0, 0)), mode='constant')
    shift = np.pad(shift, ((1, 1), (0, 0)), mode='constant')

    # Create frequency thresholds based on min and max freq
    pitches = np.zeros_like(spec)
    idx = np.argwhere(column_wise_local_max(spec, max_thresh))

    # Store pitch and magnitude
    pitches[idx[:, 0], idx[:, 1]] = ((idx[:, 0] + shift[idx[:, 0], idx[:, 1]])
                                     * float(sample_rate) / win_len)
    return pitches

def column_wise_local_max(x, thresh):
    """
    Finds the column-wise local max of an 2-D array x and returns
    a numpy list containing the indeces of the local maxes, but conditioning on values
    that are atleast within thresh of the pure columnwise max. 
    """
    x = x * (x > thresh * np.max(x, axis=0))
    pad_x = np.pad(x, [(1, 1), (0, 0)], mode='edge')
    dim_1_idx = [slice(0, -2), slice(None)]
    dim_2_idx = [slice(2, pad_x.shape[0]), slice(None)]
    column_local_max  = np.logical_and(x > pad_x[dim_1_idx], x >= pad_x[dim_2_idx])
    return column_local_max


if __name__ == "__main__":
    fs, snd = wavfile.read('samples/440_3sec.wav')
    er = detect_pitch(snd, fs)
    print(np.max(er, axis=0))
