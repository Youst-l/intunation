# intunation
Ear training game using autotune

## Web framework information
* ```pip install flask```
* Navigate to project folder, run ```export FLASK_APP=application.py``` (Linux/Mac), or ```set``` instead of ```export``` (Windows)
* Run framework with ```flask run``` (note: to quit, use Ctrl + Fn + End, not Ctrl+C)
* Navigate to http://127.0.0.1:5000/ 
* The Python server running backend is repsonsible for autotuning data ONLY, the control flow is:
	- Load exercise in JS (can create sine tones here: https://stackoverflow.com/questions/39200994/play-specific-frequency-with-javascript) (not implemented yet)
	- Record audio with HTMLAudioElement w/ JS, send to Python w/ POST, mix to mono, etc (I've implemented this)
	- Autotune audio with GET request from timestamped exercises (i.e. list of times + frequencies); return score (I am implementing this)
	- Play autotuned and raw audio to compare; update score (I am implementing now)
* To edit the autotune algs themselves, edit ```pitch_scaling``` or ```pitch_detection.py```; I've placed wrappers on all the API calls so we can edit the original code without any problem

## TODO
* Denoising input still needs work-- test bandpass filters
* Need a way to detect the start and end of audio and clip to those regions
* Need a way to toggle microphone on and off-- have mic go off for an allotted amount of time to record 
* How to handle multiple notes-- need senses of time when things change 
* Visuals need to be created 
* Port to flask immediately? 
* Need standardization of exercises-- i.e. some data structure we use to get all of the necessary info from it

