from util import *
from scipy.io import wavfile

def time_stretch_sola(fs, signal, alphas, window_len = 8192, taper_len = 2048, candid_len = 1024):
    """
    Performs time stretching on an audio signal. Uses the
    synchronized overlap-add method (SOLA).

    Inputs:
    signal: audio signal
    alpha: the factor by which to time stretch
    """
    windowed_signals = [get_windowed_signal(signal, 0, window_len, taper_len)]
    prev_offset = 0
    alpha_idx = 0
    #for i in range(1, int(len(signal)/(window_len-taper_len) * alpha)):
    #    offset = int((window_len- taper_len) * i / alpha)
    while True:
        alpha = alphas[alpha_idx][1]
        offset = prev_offset + int((window_len - taper_len) / alpha)
        if alpha_idx + 1 < len(alphas) and offset / fs >= alphas[alpha_idx+1][0]:
            alpha_idx += 1
        #offset = prev_offset + (window_len - taper_len)
        if offset >= len(signal):
            break
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

def resample(fs, signal, alphas):
    output = []
    for i, (t, alpha) in enumerate(alphas):
        start_frame = int(t * fs)
        end_frame = len(signal)
        if i+1 < len(alphas):
            end_frame = int(alphas[i+1][0] * fs)
        xi = np.arange(start_frame, end_frame)
        xf = np.arange(start_frame, end_frame, alpha)
        output = np.append(output, np.interp(xf, xi, signal[start_frame:end_frame]))
    return output

def pitch_scale(fs, snd, alphas):
    """
    Scales the pitch of the given audio file.

    Inputs:
    fs: sample rate of audio
    snd: sound to scale
    alpha: the factor by which to pitch scale
    """
    assert(snd.ndim == 1) # Only allow mono recordings
    time_stretched_signal = time_stretch_sola(fs, snd, alphas)
    return resample(fs, time_stretched_signal, alphas)
    return time_stretched_signal

if __name__ == "__main__":
    fs, snd = wavfile.read('samples/3notes_human.wav')
    signal = pitch_scale(fs, snd, [(0, 1), (1, 0.8), (2, 1.2)])
    play_signal(signal)


