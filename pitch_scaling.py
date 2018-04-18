from util import *
from scipy.io import wavfile

def time_stretch_sola(signal, alpha, window_len = 2048, taper_len = 256):
    """
    Performs time stretching on an audio signal. Uses the
    synchronized overlap-add method (SOLA).

    Inputs:
    signal: audio signal
    alpha: the factor by which to time stretch
    """
    windowed_signals = []
    for i in range(int(len(signal)/window_len * alpha)):
        offset = int((window_len - taper_len) * i / alpha)
        windowed_signal = get_windowed_signal(signal, offset, window_len, taper_len)
        windowed_signals += [windowed_signal]

    return overlap_add(windowed_signals, window_len, taper_len)
    #return signal

def get_windowed_signal(signal, t, window_len, taper_len):
    window = np.arange(0, taper_len, 1) * 1./taper_len
    window = np.append(window, np.full(window_len - 2*taper_len, 1))
    window = np.append(window, np.arange(taper_len, 0, -1) * 1./taper_len)
    return signal[t:t+window_len] * window

def overlap_add(signals, window_len, taper_len):
    output = np.zeros(len(signals) * (window_len-taper_len) + taper_len)
    for i, signal in enumerate(signals):
        offset = (window_len - taper_len) * i
        output[offset:offset+window_len] += signal
    return output

def pitch_scale(fp, alpha):
    """
    Scales the pitch of the given audio file.

    Inputs:
    signal: audio signal
    alpha: the factor by which to pitch scale
    """
    fs, snd = wavfile.read(fp)
    assert(snd.ndim == 1) # Only allow mono recordings
    return time_stretch_sola(snd, alpha)

if __name__ == "__main__":
    signal = pitch_scale('samples/3notes_human.wav', 2)
    play_signal(signal)


