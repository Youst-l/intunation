# intunation
Ear training game using autotune

## Current pitch detection 
* Implemented autocorrelation approach; works fairly well but need to tune parameters
* Beginnings of YIN algorithm implemented but isn't working super well; the autocorrelation approach as of right now seems good enough
* Implemented FFT --> parabolic interpolation approach; works well for pure tones and stringed instruments but not voice so lol

## TODO
* Denoising input still needs work-- test bandpass filters
* Need a way to detect the start and end of audio and clip to those regions
* Need a way to toggle microphone on and off-- have mic go off for an allotted amount of time to record 
* How to handle multiple notes-- need senses of time when things change 
* Visuals need to be created 
* Port to flask immediately? 
* Need standardization of exercises-- i.e. some data structure we use to get all of the necessary info from it

