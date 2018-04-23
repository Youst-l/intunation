from util import *
from scipy.io import wavfile

def time_stretch_sola(signal, alpha, window_len = 8192, taper_len = 2048, candid_len = 1024):
    """
    Performs time stretching on an audio signal. Uses the
    synchronized overlap-add method (SOLA).

    Inputs:
    signal: audio signal
    alpha: the factor by which to time stretch
    """
    windowed_signals = [get_windowed_signal(signal, 0, window_len, taper_len)]
    prev_offset = 0
    for i in range(1, int(len(signal)/(window_len-taper_len) * alpha)):
        offset = int((window_len- taper_len) * i / alpha)
        best_offset = get_best_signal_offset(signal, prev_offset, offset - candid_len, offset + candid_len, window_len)
        prev_offset = best_offset
        windowed_signal = get_windowed_signal(signal, best_offset, window_len, taper_len)
        windowed_signals += [windowed_signal]

    return overlap_add(windowed_signals, window_len, taper_len)

def get_windowed_signal(signal, t, window_len, taper_len):
    window = np.arange(0, taper_len, 1) * 1./taper_len
    window = np.append(window, np.full(window_len - 2*taper_len, 1))
    window = np.append(window, np.arange(taper_len, 0, -1) * 1./taper_len)
    trunc_signal = signal[t:t+window_len]
    return trunc_signal * window[:len(trunc_signal)]

def get_best_signal_offset(signal, prev_offset, candid_offset_low, candid_offset_high, window_len):
    prev_signal = signal[prev_offset:prev_offset+window_len]
    candid_signal = signal[candid_offset_low:candid_offset_high+window_len]
    correlation = np.correlate(prev_signal, candid_signal)
    return candid_offset_high - np.argmax(correlation)

def overlap_add(signals, window_len, taper_len):
    output = np.zeros(len(signals) * (window_len-taper_len) + taper_len)
    for i, signal in enumerate(signals):
        offset = (window_len - taper_len) * i
        output[offset:offset+len(signal)] += signal
    return output

def resample(signal, alpha):
    xi = np.arange(len(signal))
    xf = np.arange(0, len(signal), alpha)
    return np.interp(xf, xi, signal)

def pitch_scale(fs, snd, alpha):
    """
    Scales the pitch of the given audio file.

    Inputs:
    fs: sample rate of audio
    snd: sound to scale
    alpha: the factor by which to pitch scale
    """
    assert(snd.ndim == 1) # Only allow mono recordings
    time_stretched_signal = time_stretch_sola(snd, alpha)
    return resample(time_stretched_signal, alpha)

if __name__ == "__main__":
    signal = pitch_scale('samples/3notes_human.wav', 0.8)
    play_signal(signal)


