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
	- Autotune audio with GET request from timestamped exercises (i.e. list of times + frequencies); return score (I have implemented this)
	- Play autotuned and raw audio to compare; update score (Haven't dealt with score yet, but this is implemented otherwise). 
* To edit the autotune algs themselves, edit ```pitch_scaling``` or ```pitch_detection.py```; I've placed wrappers on all the API calls so we can edit the original code without any problem
* Note that there are some caching issues with the GET request to get autotune data so I recommend working in incognito mode or hard refreshing pages; we can try to find an actual non-jank solution

## TODO
* Exercises need to be created in JS
* Python autotune function needs to be smoothed out a lot
* Noise filtering at the beginning would be helpful/nice
* An actual interface cuz i don't do frontend lol 
* Duration of recording, i.e. cue that's like (you have 4 sec to record, record now)
* Way to select levels etc etc

