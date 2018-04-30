import numpy as np

from flask import Flask, render_template, request, send_file
from werkzeug.datastructures import FileStorage
from scipy.io import wavfile
from io import StringIO
from pitch_scaling import pitch_scale
from pitch_detection import detect_pitches

class Intunation(object):
	app = None

	def __init__(self):
		self.app = Flask(__name__)
		self.current_recording = np.array([])
		self.current_fs = None
		self.current_pitch_detection = None
		self.current_autotune = None
		self.app.add_url_rule('/', view_func=self.render_html)
		self.app.add_url_rule('/get_exercise', view_func=self.get_exercise, methods=['GET'])
		self.app.add_url_rule('/save_recording', view_func=self.save_recording, methods=['POST'])
		self.app.add_url_rule('/score_recording', view_func=self.score_recording, methods=['GET'])
		
	def run(self):
	    self.app.run()

	def autotune(self, exercise_cues):
		"""
		Autotunes and scores the current recording based on the cues of the given exercise.
		These cues should be formatted in the following way: a list of tuples [ (a1, b2), (a2, b2), ...]
		where (a1, b2) is a (timestamp (in seconds), note (in frequency)) pair.
		TODO: Implement with exercise cues rather than one pitch; exercise cues can be sent from JS. 
		"""
		fs, snd = self.current_fs, self.current_recording
		detected_pitches = detect_pitches(fs, snd)[0]
		true_pitch = 440.0 # needs to be changed to take in exercise cues.
		autotuned, scores, frame_lens = [], [], []
		print "DETECTED PITCHES: ", detected_pitches
		for ix, (start_time, detected_pitch) in enumerate(detected_pitches):
		    start_frame = int(start_time * fs)
		    end_frame = len(snd) if ix == len(detected_pitches) - 1 else int(detected_pitches[ix+1][0]*fs)
		    alpha = true_pitch/detected_pitch
		    scores.append(np.abs(np.log(alpha)))
		    frame_lens.append(end_frame - start_time)
		    autotuned.extend(pitch_scale(fs, snd[start_frame:end_frame], true_pitch/detected_pitch))
		autotuned = np.array(autotuned, dtype=np.int16)
		score = 1 - np.sqrt(np.average(scores, weights=frame_lens))
		return score, fs, autotuned

	def render_html(self):
	    return render_template('index.html')

	def get_exercise(self):
		pass

	def save_recording(self):
		fs, data = wavfile.read(request.files['file'])
		self.current_fs = fs
		self.current_recording = np.sum(data, axis=1) / 2
		return 'OK'
		
	def score_recording(self):
		if self.current_recording.size != 0 and self.current_fs:
			score, fs, snd = self.autotune([]) # TODO: should pass in cues after implementing autotune
			wavfile.write('autotune.wav', fs, snd)
			r = send_file('autotune.wav', mimetype='audio/wav', as_attachment=True, attachment_filename='autotune.wav')
			r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
			r.headers["Pragma"] = "no-cache"
			r.headers["Expires"] = "0"
			r.headers['Cache-Control'] = 'public, max-age=0'
			return r
		return 'BAD'
		
Intunation().run()


