// Sample exercise description; i.e. Level 0: Sing one pitch @ 440 Hz
var exampleOneNote440 = {
    times: [0.], 	// time stamps, i.e. at time 0...
    freqs: [440.],  // ... we play 440 Hz 
    level: 0,
};

// Level 1: Sing an octave interval
var exampleMajor3rd = {
    times: [0., 2.], 	  // time stamps, i.e. at time 0...
    freqs: [440., 880.],  // ... we play 440 Hz, at time 2sec we play 880
    level: 1,			  
};

var LEVEL_0 = [exampleOneNote440]; // keep variables for all exercises of a given level so we can sample randomly
var LEVEL_1 = [exampleMajor3rd];