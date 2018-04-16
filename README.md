# intunation
Ear training game using autotune

## Current pitch detection 
* Implemented autocorrelation approach; works fairly well but need to tune parameters
* Beginnings of YIN algorithm implemented but isn't working super well; the autocorrelation approach as of right now seems good enough
* Implemented FFT --> parabolic interpolation approach; works well for pure tones and stringed instruments but not voice so lol

## TODO
* How to do pitch scaling? Was thinking we get the constituent frequencies with a pure FFT, find the difference between our estimated fundamental and the one we're going for, and just multiplicatively scale up and IFFT? Curious to see how this works?
* Need to window signal in chunks in order to handle changing pitches 
* Denoising input would likely help; need to think about how to do that

### DEVANY TODO:
* Create single note pitch exercises
* Get working interface (barebones) with playing and recording audio and maybe visualizing the pitch detection

### DIVYA TODO:
* Look into smoothing audio and parameter tuning for pitch detection
* Filtering audio off the bat?
* Get microphone to work on my laptop (rip)

### JAMIE TODO:
* Start on pitch scaling (we should all discuss this together) 
* Familiarize with existing code