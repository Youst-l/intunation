// Exercise data
// Level 1: Notes
var OneNote440 = {
    times: [2.], 	// durations, i.e. for 2 seconds
    freqs: [440.],  // ... we play 440 Hz 
    level: 1,
    text: "Please sing a concert A."
};

var OneNote260 = {
    times: [2.], 	// durations, i.e. for 2 seconds
    freqs: [260.],  // ... we play 260 Hz 
    level: 1,
    text: "Please sing a middle C."
};

var OneNote466 = {
    times: [2.],  // duration
    freqs: [466.], // ... we play at 466 Hz
    level: 1,
    text: "Please sing a concert Bb."
};

var OneNote394 = {
    times: [2.],
    freqs: [394.],
    level: 1,
    text: "Please sing a concert F4."
}

// Level 2: Intervals

var Octave = {
    times: [2., 2.], 	  // durations, i.e. for 2 seconds
    freqs: [440., 880.],  // ... we play 440 Hz, at time 2sec we play 880
    level: 2,	
    text: "Please sing an A4 and then an A5.  This is an octave."		  
};

var Fifth = {
    times: [2., 2.],
    freqs: [440., 659.],
    level: 2,
    text: "Please sing an A4 and then an E4.  This is a fifth."
};

var Third = {
    times: [2.,2.],
    freqs: [440.,554.],
    level: 2,
    text: "Please sing an A4 and then a C#4.  This is a third."
};

var Fourth = {
    times: [2.,2.],
    freqs: [440.,587.],
    level: 2,
    text: "Please sing an A4 and then a D4.  This is a fourth."
};

var Seventh = {
    times: [2.,2.],
    freqs: [440.,830.],
    level: 2,
    text: "Please sing an A4 and then a G#4.  This is a seventh."
};

var Second = {
    times: [2.,2],
    freqs: [440.,494.],
    level: 2,
    text: "Please sing an A4 and then a B4.  This is a second."
};

var Sixth = {
    times: [2.,2.],
    freqs: [440.,494.],
    level: 2,
    text: "Please sing an A4 and then an F#4.  This is a sixth."
};

//Level 3: Short melodies

var HotCrossBuns = {
    times: [.5,.5,1., .5,.5,1.],
    freqs: [554.,494.,440.,554.,494.,440.],
    level: 3,
    text: "Please sing the first six notes of hot cross buns."
};

var BeethovensFifth = {
    times: [.6,.1,.6,.1,.6,.1,2.],
    freqs: [392.,0.,392.,0.,392.,0.,311.],
    level: 3,
    text: "Please sing the first four notes of Beethoven's fifth."
};

var LEVEL_1 = [OneNote440, OneNote260, OneNote466, OneNote394]; // keep variables for all exercises of a given level so we can sample randomly
var LEVEL_2 = [Octave, Fifth, Third, Fourth, Seventh, Second, Sixth];
var LEVEL_3 = [HotCrossBuns, BeethovensFifth];
var EXERCISES = [LEVEL_1, LEVEL_2, LEVEL_3];
var LEVEL_TEXT_MAP = ["Level 1: Pitch", "Level 2: Interval", "Level 3: Melody"];