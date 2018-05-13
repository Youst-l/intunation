// Exercise data
// Vocal range: keep things between a G3 and a B4!

// Level 1: Pitch Matching

// 1.1
var OneNote220 = {
    times: [2.], 	// durations, i.e. for 2 seconds
    freqs: [220.],  // ... we play 220 Hz 
    level: 1,
    text: "Please sing an A3."
};

// 1.2
var OneNote277 = {
    times: [2.], 	
    freqs: [277.],  
    level: 1,
    text: "Please sing a C#4."
};

// 1.3
var OneNote415 = {
    times: [2.],
    freqs: [415.],
    level: 1,
    text: "Please sing a G#4."
};

// 1.4
var OneNote329 = {
    times: [2.],
    freqs: [329.],
    level: 1,
    text: "Please sing an E4."
};

// 1.5
var OneNote293 = {
    times: [2.],
    freqs: [293.],
    level: 1,
    text: "Please sing a D4."
};

// Level 2: Introducing Intervals: octave, fifth, and third

// 2.1
var TonicA3 = {
    times: [2.],
    freqs: [220.],
    level: 2,
    text: "Please sing an A3.  This will be our tonic note."
};

// 2.2
var TonicA4 = {
    times: [2.],
    freqs: [440.],
    level: 2,
    text: "Please sing one octave up from the A3."
};

// 2.3
var Octave = {
    times: [2., 2.],
    freqs: [220., 440.],  
    level: 2,	
    text: "Please sing an A3 and then an A4.  This is an octave."		  
};

// 2.4
var FifthE4 = {
    times: [2.],
    freqs: [329.],
    level: 2,
    text:  "Please sing an E4.  This is the fifth note in our scale."
};

// 2.5
var Fifth = {
    times: [2., 2.],
    freqs: [220., 329.],
    level: 2,
    text: "Please sing an A3 and then an E4.  This is a fifth."
};

// 2.6
var ThirdCSharp4 = {
    times: [2.],
    freqs: [277.],
    level: 2,
    text: "Please sing a C#4.  This is the third note in our scale."
} 

// 2.7
var Third = {
    times: [2.,2.],
    freqs: [220., 277.],
    level: 2,
    text: "Please sing an A3 and then a C#4.  This is a third."
};

// Level 3: More Intervals

// 3.1  Tonic will come first to restablish key.
var TonicA3_3 = {
    times: [2.],
    freqs: [220.],
    level: 3,
    text: "Please sing the tonic note, A3."
};

// 3.2
var FourthD4 = {
    times: [2.],
    freqs: [293.],
    level: 3,
    text: "Please sing a D4.  This is the fourth note in our scale."
};

// 3.3
var Fourth = {
    times: [2.,2.],
    freqs: [220.,293.],
    level: 3,
    text: "Please sing an A3 and then a D4.  This is a fourth."
};

// 3.4
var SeventhGSharp3 = {
    times: [2.],
    freqas: [415.],
    level: 3,
    text: "Please sing a G#4.  This is the seventh note in our scale."
};

// 3.5
var Seventh = {
    times: [2.,2.],
    freqs: [220.,415.],
    level: 3,
    text: "Please sing an A3 and then a G#4.  This is a seventh."
};

// 3.6
var SecondB3 = {
    times: [2.],
    freqs: [246.],
    level: 3,
    text: "Please sing a B3.  This is the second note in our scale."
};

// 3.7
var Second = {
    times: [2.,2],
    freqs: [240.,246.],
    level: 3,
    text: "Please sing an A3 and then a B3.  This is a second."
};

// 3.8
var SixthFSharp4 = {
    times: [2.],
    freqs: [369.],
    level: 3,
    text: "Please sing an F#4.  This is the sixth note in our scale."
};

// 3.9
var Sixth = {
    times: [2.,2.],
    freqs: [220.,369.],
    level: 3,
    text: "Please sing an A3 and then an F#4.  This is a sixth."
};

//Level 4: Short melodies

// 4.1
var HotCrossBuns = {
    times: [.5,.5,1.,.5,.5,1.],
    freqs: [554.,494.,440.,554.,494.,440.],
    level: 4,
    text: "Please sing the first six notes of hot cross buns."
};

// 4.2
var Twinkle = {
    times: [.5,.5,.5,.5,.5,.5,1.],
    freqs: [220.,220.,329.,329.,369.,369.,329.],
    level: 4,
    text: "Please sing the first seven notes of twinkle twinkle."
};

// 4.3
var BeethovensFifth = {
    times: [.6,.1,.6,.1,.6,.1,2.],
    freqs: [392.,0.,392.,0.,392.,0.,311.],
    level: 3,
    text: "Please sing the first four notes of Beethoven's fifth."
};

var LEVEL_1 = [OneNote220, OneNote277, OneNote415, OneNote329, OneNote293]; // keep variables for all exercises of a given level so we can sample randomly
var LEVEL_2 = [TonicA3, TonicA4, Octave, FifthE4, Fifth, ThirdCSharp4, Third];
var LEVEL_3 = [TonicA3_3, FourthD4, Fourth, SeventhGSharp3, Seventh, SecondB3, Second, SixthFSharp4, Sixth]
var LEVEL_4 = [HotCrossBuns, Twinkle, BeethovensFifth];
var EXERCISES = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4];
var LEVEL_TEXT_MAP = ["Level 1: Pitch matching", "Level 2: Introducing Intervals", "Level 3: More Intervals", "Level 4: Melodies"];