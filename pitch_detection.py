from util import *
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, lfilter
import matplotlib.pyplot as plt

def detect_pitch_parabolic(signal, fs):
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
    signal -= np.mean(signal)  # Remove DC offset
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
    dskew = 0.5 * avg * shift

    # Create frequency thresholds based on min and max freq
    pitches = np.zeros_like(spec)
    magnitudes = np.zeros_like(spec)
    idx = np.argwhere(column_wise_local_max(spec, max_thresh))

    # Store pitch and magnitude
    pitches[idx[:, 0], idx[:, 1]] = ((idx[:, 0] + shift[idx[:, 0], idx[:, 1]])
                                     * float(sample_rate) / win_len)

    magnitudes[idx[:, 0], idx[:, 1]] = (spec[idx[:, 0], idx[:, 1]]
                                  + dskew[idx[:, 0], idx[:, 1]])
    return pitches[np.argmax(magnitudes, axis=0)]

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

def detect_pitch_autocorr(signal, fs):
    """
    Calculate autocorrelation efficiently using an FFT convolution.
    Use parabolic interpolation on local maxes of autocorrelation 
    to find true fundamental frequencies (better for voice).

    Inputs:
    signal: audio signal
    fs: sample rate of audio signal
    """
    signal = np.subtract(signal, np.mean(signal)) # Remove DC offset
    corr = fftconvolve(signal, signal[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first peak on the left
    peaks = find_peaks(corr)
    interp_peak = parabolic_interp(corr, peaks)[0]
    return fs/interp_peak

def detect_pitches(fp, window_len=2048, thresh=30):
    """
    Detects pitches given a filepath to the audio sample in question.
    Returns a list of tuples [(a1, b1), (a2, b2), ...] representing (frequency, time) pairs of the pitch.

    Inputs:
    fp: filepath of audio to pitch detect on
    window_len: number of samples to window audio file over
    thresh: threshold in Hz of when to classify a new pitch as "different"

    """
    # Load signal and clean it with filtering
    fs, snd = wavfile.read(fp)
    assert(snd.ndim == 1) # Only allow mono recordings
    # Pitch detect in windows
    octave_thresh = 5
    all_pitches = []
    pitches = [(0, 0)]
    for i in range(0, len(snd), window_len):
        sig = snd[i:min(len(snd), i+window_len)]
        possible_pitches = detect_pitch_autocorr(sig, fs)
        pitch = possible_pitches[0]
        last_pitch = pitches[-1][1]
        # Edge case 1: too much of a shift in freq
        if len(possible_pitches) > 1 and i != 0 and np.abs(pitch - last_pitch) > np.abs(last_pitch - possible_pitches[1]) \
         and np.abs((possible_pitches[1] / pitch) - 2) < octave_thresh : 
            pitch = possible_pitches[1]
        all_pitches.append((float(i)/float(fs), pitch))
        if np.abs(pitch - last_pitch) >= thresh:
            pitches.append((float(i)/float(fs), pitch))
    return pitches[1:], all_pitches # get rid of dummy pitch at beginning



if __name__ == "__main__":
    p, all_pitch = detect_pitches('samples/440_human.wav')
    plt.scatter(*zip(*all_pitch))
    plt.ylim((0, 1000))
    plt.xlabel("Time in audio (sec)")
    plt.ylabel("Pitch detected (Hz)")
    plt.show()


# CODE BELOW IS NOT FUNCTIONAL BUT IS ME (INEFFICIENTLY) IMPLEMENTING YIN

# def yin_pitch_detection(signal, fs):
#     # PARAMETERS 
#     sample_rate = float(fs)
#     freq_min, freq_max = 40, 4000 # frequency range of human voice in Hz 
#     win_len = 4096
#     hop_size = win_len / 4
#     max_thresh = 0.1
#     eps = 0.0000001

#     # Get spectrogram (magnitude STFT) from audio signal and the constituent freqs
#     signal -= np.mean(signal)  # Remove DC offset
#     spec = stft_mag(signal, win_len, hop_size)
#     k = np.arange(len(signal))
#     T = len(signal)/fs
#     frqLabel = k/T

#     # Step 2: Get differences of autocorrelation
#     tau_max = 3000
#     win_size = 6000
#     r = np.zeros(tau_max)
#     for tau in range(tau_max):
#         s = 0.
#         for j in range(win_len):
#             s += (signal[j] - signal[j+tau])**2
#         r[tau] = s

#     # Step 3: Cumulative mean normalized difference function
#     d = np.zeros(tau_max)
#     s = r[0]
#     d[0] = 1
#     for tau in range(1,tau_max):
#         s += r[tau]
#         d[tau] = r[tau] / ((1 / tau) * s) 

#     for i in range(tau_max):
#         if d[i] > 0.5:
#             continue
#         if d[i-1] > d[i] < d[i+1]:
#             print(44100/i)
#             break
