// Sample exercise description; i.e. Level 0: Sing one pitch @ 440 Hz
var exampleOneNote440 = {
    times: [2.], 	// durations, i.e. for 2 seconds
    freqs: [440.],  // ... we play 440 Hz 
    level: 1,
    text: "Please sing a concert A."
};

// Sample exercise description; i.e. Level 0: Sing one pitch @ 440 Hz
var exampleOneNote260 = {
    times: [2.], 	// durations, i.e. for 2 seconds
    freqs: [260.],  // ... we play 260 Hz 
    level: 1,
    text: "Please sing a middle C."
};

// Level 1: Sing an octave interval
var exampleOctave = {
    times: [2., 2.], 	  // durations, i.e. for 2 seconds
    freqs: [440., 880.],  // ... we play 440 Hz, at time 2sec we play 880
    level: 2,	
    text: "Please sing an A4 and then an A5."		  
};

var LEVEL_1 = [exampleOneNote440, exampleOneNote260]; // keep variables for all exercises of a given level so we can sample randomly
var LEVEL_2 = [exampleOctave];
var LEVEL_3 = [];
var EXERCISES = [LEVEL_1, LEVEL_2, LEVEL_3];
var LEVEL_TEXT_MAP = ["Level 1: Pitch", "Level 2: Interval", "Level 3: Melody"];