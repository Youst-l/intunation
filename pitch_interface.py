
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
from common.synth import *
from common.clock import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock
from pitch_detection import detect_pitches
from pitch_scaling import pitch_scale
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
        self.audio = Audio(2, input_func=self.writer.add_audio)
        self.synth = Synth("data/FluidR3_GM.sf2")
        self.audio.set_generator(self.synth)
        self.synth.program(0, 0, 46)
        self.score_val = 0

        self.notes = ['C','Db','D','Eb','F','Gb','G','Ab','A','Bb','B']
        self.pitches = [60,61,62,63,64,65,66,67,68,69,70,71]
        self.note = self.rand_note()
        self.pitch = self.pitches[self.notes.index(self.note)]

        self.note_label = Label(text='Sing a concert ' + self.note, pos=(Window.width / 2, Window.height * 5 / 6))
        self.record_label = Label(text='Press r to record.', pos=(Window.width/2, Window.height * 4 / 6))
        self.play_label = Label(text='Press p to play the note.', pos=(Window.width/2, Window.height * 3 / 6))
        self.score_label = Label(text='Press s to score your recording.', pos=(Window.width/2, Window.height* 2 / 6))
        self.add_widget(self.play_label)
        self.add_widget(self.note_label)
        self.add_widget(self.record_label)
        self.add_widget(self.score_label)
        
        self.info = topleft_label()
        self.add_widget(self.info)
        self.on_update()

    def play_note(self):
        print 'note playing'
        self.synth.noteon(0,self.pitch,100)

    def record(self):
        print 'recording'
        self.writer.toggle()

    def score(self):
        self.detected_pitches = detect_pitches('samples/440_human.wav')
        note_num = self.convert_hz_to_note(440.0)
        self.score_val += self.pitch - note_num

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

    def on_update(self):
        self.objects.on_update()
        self.audio.on_update()
        self.info.text = 'Score:  ' + str(self.score_val)

class BeatBubble(InstructionGroup):
    def __init__(self, input_note, true_note):
        super(BeatBubble,self).__init__()
        self.input_note = input_note
        self.true_note = true_note

#TODO: Idea for a graphical display of the *beating* that happens when two notes 
# are just slightly out of tune to teach people how to listen for that interference
# If I can't at least attempt to implement this by this milestone, I'll get it done by MS2


run(MainWidget)