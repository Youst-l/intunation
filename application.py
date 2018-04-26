from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from scipy.io import wavfile

app = Flask(__name__)

current_recording = None
current_fs = None
current_pitch_detection = None
current_autotune = None

@app.route('/')
def render_html():
    return render_template('index.html')

@app.route('/get_exercise', methods=['GET'])
def get_exercise():
	pass

@app.route('/save_recording', methods=['POST'])
def save_recording():
	current_fs, data = wavfile.read(request.files['file'])
	current_recording = np.sum(data, axis=1) / 2
	return 'OK'

@app.route('/score_recording', methods=['GET'])
def score_recording():
	pass
