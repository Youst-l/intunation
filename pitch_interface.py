import sys
import random
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.writer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.clock import *
from common.note import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock
from pitch_detection import detect_pitches
from pitch_scaling import pitch_scale
from scipy.io import wavfile
from math import log

# Read data from Divya's pitch_detection.py list of tuples (time,hz)
# Come up with visual feedback for this information
# Have a way to play back the audio data from the .wav files

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget,self).__init__()
        self.objects = AnimGroup()
        self.canvas.add(self.objects)
        self.writer = AudioWriter('data')
        self.audio = Audio(1, input_func=self.writer.add_audio)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.score_val = 0

        self.notes = ['C','Db','D','Eb','F','Gb','G','Ab','A','Bb','B']
        self.pitches = [60,61,62,63,64,65,66,67,68,69,70,71]
        self.note = 'A' #self.rand_note()
        self.pitch = self.pitches[self.notes.index(self.note)]

        self.note_label = Label(text='Sing a concert ' + self.note, pos=(Window.width / 2, Window.height * 5 / 6))
        self.record_label = Label(text='Press r to record.', pos=(Window.width/2, Window.height * 4 / 6))
        self.play_label = Label(text='Press p to play the note.', pos=(Window.width/2, Window.height * 3 / 6))
        self.score_label = Label(text='Press a to score your recording.', pos=(Window.width/2, Window.height* 2 / 6))
        self.play_record_label = Label(text='Press x to play recording, y to play autotune.', pos=(Window.width/2, Window.height / 6))
        self.add_widget(self.play_label)
        self.add_widget(self.note_label)
        self.add_widget(self.record_label)
        self.add_widget(self.score_label)
        self.add_widget(self.play_record_label)
        
        self.info = topleft_label()
        self.add_widget(self.info)
        self.on_update()

    def play_note(self):
        print 'note playing'
        self.note = NoteGenerator(69.0,1.0,1.0)
        self.mixer.add(self.note)

    def record(self):
        print 'recording'
        self.writer.toggle()

    def play_autotune(self):
        self.autotune_wav = WaveGenerator(WaveFile('data_autotuned1.wav'))
        self.mixer.add(self.autotune_wav)

    def play_recording(self):
        self.recording_wav = WaveGenerator(WaveFile('data1.wav'))
        self.mixer.add(self.recording_wav)

    def score(self):
        self.detected_pitches = detect_pitches('data1.wav')[0]
        print "DETECTED PITCHES: ", self.detected_pitches
        note_num = self.convert_hz_to_note(440.0)

    def autotune(self):
        fs, snd = wavfile.read('data1.wav')
        true_pitch = 440.0
        self.score()
        autotuned, scores, frame_lens = [], [], []
        for ix, (start_time, detected_pitch) in enumerate(self.detected_pitches):
            start_frame = int(start_time * fs)
            end_frame = len(snd) if ix == len(self.detected_pitches) - 1 else int(self.detected_pitches[ix+1][0]*fs)
            alpha = true_pitch/detected_pitch
            print "ALPHAS: ", alpha
            scores.append(np.abs(np.log(alpha)))
            frame_lens.append(end_frame - start_time)
            autotuned.extend(pitch_scale(fs, snd[start_frame:end_frame], true_pitch/detected_pitch))
        autotuned = np.array(autotuned, dtype=np.int16)
        #autotuned /= np.max(np.abs(autotuned))
        score = 1 - np.average(scores, weights=frame_lens)
        self.score_val += score
        wavfile.write('data_autotuned1.wav', fs, autotuned)
        return autotuned

    def rand_note(self):
        return self.notes[random.randint(0,len(self.notes)-1)]

    def convert_hz_to_note(self, hz):
        return 69.0 + 12*log(hz/440.0,2)

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'r':
            self.record()
        if keycode[1] == 'p':
            self.play_note()
        if keycode[1] == 's':
            self.score()
        if keycode[1] == 'a':
            self.autotune()
        if keycode[1] == 'x':
            self.play_recording()
        if keycode[1] == 'y':
            self.play_autotune()

    def on_update(self):
        self.objects.on_update()
        self.audio.on_update()
        self.info.text = 'Score:  ' + "{0:.2f}".format(self.score_val)

class BeatBubble(InstructionGroup):
    def __init__(self, input_note, true_note):
        super(BeatBubble,self).__init__()
        self.input_note = input_note
        self.true_note = true_note

#TODO: Idea for a graphical display of the *beating* that happens when two notes 
# are just slightly out of tune to teach people how to listen for that interference
# If I can't at least attempt to implement this by this milestone, I'll get it done by MS2


run(MainWidget)