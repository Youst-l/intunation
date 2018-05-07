from util import *
from scipy.io import wavfile

from pitch_detection import detect_pitches
from pitch_scaling import pitch_scale

def autotune_and_score(fs, snd, cues):
    print "CUES:", cues
    pitches = detect_pitches(fs, snd)[0]
    print "PITCHES:", pitches
    pitch_idx = 0
    cue_idx = 0
    alphas = [(0, cues[cue_idx][1]/pitches[pitch_idx][1])]
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
        alpha = cues[cue_idx][1]/pitches[pitch_idx][1]
        #while alpha > 2 ** 0.5:
        #    alpha /= 2
        #while alpha < 2 ** -0.5:
        #    alpha *= 2
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
    return pitch_scale(fs, snd, alphas), score/2.

if __name__ == "__main__":
    fs, snd = wavfile.read('samples/3notes_human.wav')
    autotuned_signal, score = autotune_and_score(fs, snd, [(0, 440)])
    print score
    #play_signal(autotuned_signal)
