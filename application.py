import numpy as np

from flask import Flask, render_template, request, send_file, make_response
from werkzeug.datastructures import FileStorage
from scipy.io import wavfile
from pitch_autotune import autotune_and_score

class Intunation(object):
	app = None

	def __init__(self):
		self.app = Flask(__name__)
		self.current_recording = np.array([])
		self.current_fs = None
		self.current_pitch_detection = None
		self.current_autotune = None
		self.score = 0 
		self.current_exercise = None # tuple (freqs, dur) of frequencies and associated durations
		self.app.add_url_rule('/', view_func=self.render_html)
		self.app.add_url_rule('/get_exercise', view_func=self.get_exercise, methods=['GET'])
		self.app.add_url_rule('/save_recording', view_func=self.save_recording, methods=['POST'])
		self.app.add_url_rule('/score_recording', view_func=self.score_recording, methods=['GET'])
		self.app.add_url_rule('/score', view_func=self.get_score, methods=['GET'])
		
	def run(self):
	    self.app.run()

	def autotune(self, exercise):
		"""
		Autotunes and scores the current recording based on the cues of the given exercise.
		These cues should be formatted in the following way: a list of tuples [ (a1, b2), (a2, b2), ...]
		where (a1, b2) is a (timestamp (in seconds), note (in frequency)) pair.
		"""
		print "EXERCISE:", exercise
		exercise_cues = []
		t = 0
		for i in range(len(exercise[0])):
			exercise_cue = (t, exercise[0][i])
			t += exercise[1][i]
			exercise_cues += [exercise_cue]

		fs, snd = self.current_fs, self.current_recording
		autotuned, score = autotune_and_score(fs, snd, exercise_cues)
		autotuned = np.array(autotuned, dtype=np.int16)
		return score, fs, autotuned

	def render_html(self):
	    return render_template('index.html')

	def get_exercise(self):
		pass

	def save_recording(self):
		fs, data = wavfile.read(request.files['file'])
		freq_string = request.form['freqs'].encode('utf-8')[1:-1].split(",")
		dur_string = request.form['times'].encode('utf-8')[1:-1].split(",")
		self.current_exercise = ([float(i) for i in freq_string], [float(i) for i in dur_string])
		self.current_fs = fs
		self.current_recording = np.sum(data, axis=1) / 2
		return 'OK'

	def get_score(self):
		return make_response("%0.2f" % (self.score))
		
	def score_recording(self):
		if self.current_recording.size != 0 and self.current_fs:
			score, fs, snd = self.autotune(self.current_exercise) # TODO: should pass in cues after implementing autotune
			self.score += score
			wavfile.write('autotune.wav', fs, snd)
			r = send_file('autotune.wav', mimetype='audio/wav', as_attachment=True, attachment_filename='autotune.wav')
			r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
			r.headers["Pragma"] = "no-cache"
			r.headers["Expires"] = "0"
			r.headers['Cache-Control'] = 'public, max-age=0'
			return r
		return 'BAD'
		
Intunation().run()


