from util import *
from scipy.io import wavfile

def time_stretch_sola(fs, signal, alpha, window_len = 8192, taper_len = 2048, candid_len = 1024):
    """
    Performs time stretching on an audio signal. Uses the
    synchronized overlap-add method (SOLA).

    Inputs:
    signal: audio signal
    alpha: the factor by which to time stretch
    """
    signals = [(0, signal[:window_len])]
    prev_offset = 0
    for i in range(1, int(len(signal)/(window_len-taper_len) * alpha)):
        offset = int((window_len- taper_len) * i / alpha)
        if offset >= len(signal):
            break
        best_offset = get_best_signal_offset(signal, prev_offset, offset - candid_len, offset + candid_len, window_len)
        prev_offset = best_offset
        signals += [(offset, signal[best_offset:best_offset+window_len])]

    return overlap_add(signals, taper_len)

def get_best_signal_offset(signal, prev_offset, candid_offset_low, candid_offset_high, window_len):
    prev_signal = signal[prev_offset:prev_offset+window_len]
    candid_signal = signal[candid_offset_low:candid_offset_high+window_len]
    correlation = np.correlate(prev_signal, candid_signal)
    return candid_offset_high - np.argmax(correlation)

def apply_window_right(signal, t, taper_len):
    window = np.full(t, 1)
    window = np.append(window, np.arange(taper_len, 0, -1) * 1./taper_len)
    window = np.append(window, np.full(max(len(signal) - len(window), 0), 0))
    return signal * window[:len(signal)]

def apply_window_left(signal, t, taper_len):
    window = np.arange(0, taper_len, 1) * 1./taper_len
    window = np.append(window, np.full(max(len(signal) - len(window), 0), 1))
    return signal * window[:len(signal)]

def overlap_add(signals, taper_len):
    output = signals[0][1]
    for (t, signal) in signals[1:]:
        output = np.append(output, np.full(max(t + len(signal) - len(output), 0), 0))
        output = apply_window_right(output, t, taper_len)
        output[t:t+len(signal)] += apply_window_left(signal, t, taper_len)
    return output

def resample(fs, signal, alpha):
    xi = np.arange(0, len(signal))
    xf = np.arange(0, len(signal), alpha)
    return np.interp(xf, xi, signal)

def scale_pitch_one_alpha(fs, snd, alpha):
    time_stretched_signal = time_stretch_sola(fs, snd, alpha)
    resampled_signal = resample(fs, time_stretched_signal, alpha)
    return resampled_signal

def scale_pitch_many_alphas(fs, snd, alphas, taper_len = 2048):
    signals = []
    for (t, alpha) in alphas:
        frame = int(t * fs)
        signal = scale_pitch_one_alpha(fs, snd[frame:], alpha)
        signals += [(frame, signal)]
    return overlap_add(signals, taper_len)

def pitch_scale(fs, snd, alphas):
    """
    Scales the pitch of the given audio file.

    Inputs:
    fs: sample rate of audio
    snd: sound to scale
    alpha: the factor by which to pitch scale
    """
    assert(snd.ndim == 1) # Only allow mono recordings
    return scale_pitch_many_alphas(fs, snd, alphas)

if __name__ == "__main__":
    fs, snd = wavfile.read('samples/3notes_human.wav')
    signal = pitch_scale(fs, snd, [(0, 1), (1, 0.8), (2, 1.2), (3, 1)])
    play_signal(signal)


