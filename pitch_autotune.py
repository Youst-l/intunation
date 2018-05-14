from util import *
from scipy.io import wavfile

from pitch_detection import detect_pitches
from pitch_scaling import pitch_scale

def normalize_alpha(alpha):
    if alpha <= 0:
        return 0
    while alpha > 2 ** 0.5:
        alpha /= 2
    while alpha < 2 ** -0.5:
        alpha *= 2
    return alpha

def autotune_and_score(fs, snd, cues):
    print "CUES:", cues
    all_pitches, pitches = detect_pitches(fs, snd)
    print "PITCHES:", pitches
    pitch_idx = 0
    cue_idx = 0
    new_cues = []
    for i, cue in enumerate(cues):
        if i == 0:
            new_cues += [cue]
            continue
        min_t = cue[0] - 0.05
        max_t = cue[0] + 0.30
        max_diff = 0
        best_t = cue[0]
        for i in range(len(pitches)):
            if i == 0:
                continue
            t = pitches[i][0]
            if t < min_t or t > max_t:
                continue
            diff = pitches[i][1] / pitches[i-1][1]
            if diff < 1:
                diff = 1./diff
            if diff > max_diff:
                max_diff = diff
                best_t = t
        new_cues += [(best_t, cue[1])]
    cues = new_cues
    print "ADJUSTED CUES:", cues
    alphas = [(0, normalize_alpha(cues[cue_idx][1]/pitches[pitch_idx][1]))]
    while True:
        if pitch_idx+1 < len(pitches):
            if cue_idx+1 < len(cues):
                if pitches[pitch_idx+1][0] < cues[cue_idx+1][0]:
                    pitch_idx += 1
                else:
                    cue_idx += 1
            else:
                pitch_idx += 1
        else:
            if cue_idx+1 < len(cues):
                cue_idx += 1
            else:
                break
        t = max(pitches[pitch_idx][0], cues[cue_idx][0])
        alpha = normalize_alpha(cues[cue_idx][1]/pitches[pitch_idx][1])
        alphas += [(t, alpha)]
    print "ALPHAS:", alphas

    scores = []
    frame_lens = []
    for i in range(len(alphas)):
        scores += [np.abs(np.log(alphas[i][1]))]
        frame_len = 0
        if i+1 < len(alphas):
            frame_len = alphas[i+1][0] - alphas[i][0]
        else:
            frame_len = len(snd)*1./fs - alphas[i][0]
        frame_len = max(frame_len, 0)
        frame_lens += [frame_len]
    
    score = max(1 - np.average(scores, weights=frame_lens), 0.)
    print "SCORE:", score
    return pitch_scale(fs, snd, alphas)[:len(snd)], score, all_pitches
if __name__ == "__main__":
    fs, snd = wavfile.read('samples/3notes_human.wav')
    autotuned_signal, score = autotune_and_score(fs, snd, [(0, 440)])
    print score
