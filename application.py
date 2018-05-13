import numpy as np

from scipy.io import wavfile
from flask import Flask, render_template, request, send_file, make_response, send_from_directory, jsonify
from werkzeug.datastructures import FileStorage
from pitch_autotune import autotune_and_score

class Intunation(object):
	app = None

	def __init__(self):
		self.app = Flask(__name__)
		self.current_recording = np.array([])
		self.current_fs = None
		self.current_pitch_detection = None
		self.score = 0 
		self.current_exercise = None # tuple (freqs, dur) of frequencies and associated durations
		self.app.add_url_rule('/', view_func=self.render_html)
		self.app.add_url_rule('/favicon.png', view_func=self.favicon, methods=['GET'])
		self.app.add_url_rule('/save_recording', view_func=self.save_recording, methods=['POST'])
		self.app.add_url_rule('/score_recording', view_func=self.score_recording, methods=['GET'])
		self.app.add_url_rule('/score', view_func=self.get_score, methods=['GET'])
		self.app.add_url_rule('/get_pitches', view_func=self.get_pitches, methods=['GET'])
		self.app.add_url_rule('/serve_metronome', view_func=self.serve_metronome, methods=['GET'])
		self.app.add_url_rule('/serve_level_complete', view_func=self.serve_level_complete, methods=['GET'])
		self.app.add_url_rule('/serve_exercise_complete', view_func=self.serve_exercise_complete, methods=['GET'])
		
	def run(self):
	    self.app.run()

	def favicon(self):
		return send_from_directory('data/', 'favicon.png')

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
		autotuned, score, pitches = autotune_and_score(fs, snd, exercise_cues)
		autotuned = np.array(autotuned, dtype=np.int16)
		return score, fs, autotuned, pitches

	def render_html(self):
	    return render_template('index.html')

	def serve_metronome(self):
		return send_from_directory('data/', 'click.wav')

	def serve_level_complete(self):
		return send_from_directory('data/', 'level_complete.wav')

	def serve_exercise_complete(self):
		return send_from_directory('data/', 'exercise_complete.wav')

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

	def get_pitches(self):
		points = [{'x' : 0, 'y' : self.current_pitch_detection[0][1] }] 
		for time, freq in self.current_pitch_detection:
			points.append({ 'x' : time, 'y' : freq })
		print self.current_exercise
		points.append({'x' : sum(self.current_exercise[1]), 'y':points[-1]['y']})
		print points
		return make_response(jsonify(points))
		
	def score_recording(self):
		if self.current_recording.size != 0 and self.current_fs:
			score, fs, snd, pitches = self.autotune(self.current_exercise) 
			self.current_pitch_detection = pitches
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


