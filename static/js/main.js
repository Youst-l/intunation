var RECORDING = false;
var audio_context;
var canvasContext;
var analyzer;
var meter;
var gauge;
var current_level;
var current_exercise_num;
var recorded_audio;
var autotuned_audio;
var username;
var level;
var wavesurferRecorded;
var wavesurferAutotuned
var NUM_LEVELS = 4;
var metronome = new Audio('/serve_metronome');
var level_complete_snd = new Audio('/serve_level_complete');
var exercise_complete_snd = new Audio('/serve_exercise_complete');
var rafID = null;

$( document ).ready(function() {
    console.log( "ready!" );
    clearAudio();
    canvasContext = $("#meter")[0].getContext('2d');
    canvasContext.canvas.width  = 50;
  	canvasContext.canvas.height = 20;
    $("#instructions").hide();
    $("#progressTimer").hide();
    $('#signin').modal({backdrop: 'static', keyboard: false})
	$.each(LEVEL_TEXT_MAP, function(index, value) {
	    $("#level-select").append($("<option />").html(value));
	});
    $('#complete-level').modal({backdrop: 'static', keyboard: false})
    $('#complete-level').modal('hide');
    $( "#record-btn" ).click(function() { 
	  if (RECORDING) { stopRecording(); }
	  else { startRecordingOnTimer(); }
	});
	$( "#autotune-btn" ).click(function() { 
		if (recorded_audio && !autotuned_audio) { 
			getAutotune(); 
			$('#ok-btn').prop('disabled', false);
		}
	});
	$( "#ok-btn" ).click(function() { completeExercise(); });
	$( "#play-btn" ).click(function() { playExercise(); });
	$( "#signin-btn" ).click( function() { signIn(); });
	$( "#complete-level-btn" ).click(function() { 
		var cur_level_num = current_level[0].level;
		completeLevel(cur_level_num);
		$('#progress').text("");
		$('#complete-level').modal('hide');
	});
	$( ".wavesurferPlay" ).click(function() { 
		$(this).find('i').toggleClass('glyphicon glyphicon-arrow-pause').toggleClass('glyphicon glyphicon-arrow-play');
	});
	var opts = {
	  angle: 0.15, // The span of the gauge arc
	  lineWidth: 0.44, // The line thickness
	  radiusScale: 1, // Relative radius
	  pointer: {
	    length: 0.6, // // Relative to gauge radius
	    strokeWidth: 0.035, // The thickness
	    color: '#000000' // Fill color
	  },
	  limitMax: false,     // If false, max value increases automatically if value > maxValue
	  limitMin: false,     // If true, the min value of the gauge will be fixed
	  colorStart: '#6FADCF',   // Colors
	  colorStop: '#8FC0DA',    // just experiment with them
	  strokeColor: '#E0E0E0',  // to see which ones work best for you
	  generateGradient: true,
	  highDpiSupport: true,     // High resolution support
	  
	};
	gauge = new Gauge($("#meter")[0]).setOptions(opts);
	gauge.maxValue = 100; // set max gauge value
	gauge.setMinValue(0);  // Prefer setter over gauge.minValue = 0
	gauge.animationSpeed = 32; // set animation speed (32 is default value)
	gauge.set(50); // set actual value
	$('#signin').modal('show');
});

/**
 * Starts the recording process by requesting the access to the microphone.
 * Then, if granted proceed to initialize the library and store the stream.
 *
 * It only stops when the method stopRecording is triggered.
 */
function startRecording() {
	clearAudio();
	$('#record-btn').prop('disabled', false);
	console.log("STARTING")
	RECORDING = true;
	$("#record-btn").removeClass("btn btn-record").addClass("btn btn-danger"); 
	$("#recordingCue").empty();
	var sum = current_level[current_exercise_num].times.reduce(function (accumulator, currentValue) { return accumulator + currentValue; }, 0);
    $("#progressTimer").progressTimer({
    	timeLimit: sum,
    	warningThreshold: 10,
    	baseStyle: 'progress-bar-warning',
    	warningStyle: 'progress-bar-danger',
    	completeStyle: 'progress-bar-info',
    	onFinish: function() {
    		stopRecording();
    		setTimeout(function() { $("#progressTimer").hide(); }, 1000);
    	}
    });
    recorder && recorder.record();
    console.log('Recording...');
    $("#progressTimer").show();
}

/**
 * Stops the recording process. The method expects a callback as first
 * argument (function) executed once the AudioBlob is generated and it
 * receives the same Blob as first argument. The second argument is
 * optional and specifies the format to export the blob either wav or mp3
 */
function stopRecording() {
	RECORDING = false;
    // Stop the recorder instance
    recorder && recorder.stop();
    console.log('Stopped recording.');

    // Stop the getUserMedia Audio Stream !
    //audio_stream.getAudioTracks()[0].stop();
    recorder && recorder.exportWAV(function (blob) {
            var audioUrl = URL.createObjectURL(blob);
            recorded_audio = new Audio(audioUrl);
			wavesurferRecorded.loadBlob(blob);
			$( "#wsRPlay" ).prepend("<button class=\"btn btn-primary wavesurferPlay\" onclick=\"wavesurferRecorded.playPause()\"><i class=\"glyphicon glyphicon-record\"></i><i class=\"glyphicon glyphicon-play\"></i></button>");
            recorded_audio.crossOrigin="anonymous";
            sendRecording(blob);
            recorder.clear();
        }, "audio/wav");
    $("#record-btn").removeClass("btn btn-danger").addClass("btn btn-record"); 
	$('#autotune-btn').prop('disabled', false);
}

/**
Sends recording with an AudioBlob file attachment.
POST request received by Flask and handled internally server-side.
*/
sendRecording = function(blob) {
	var formData = new FormData()
	formData.append('freqs', JSON.stringify(current_level[current_exercise_num].freqs));
    formData.append('times', JSON.stringify(current_level[current_exercise_num].times));
    formData.append('file', blob, 'audio') 
	$.ajax({
	  type: "POST",
	  url: "/save_recording",
	  data: formData,
	  processData: false,
	  contentType: false, 
	  cache: false
	});            
}

function getAutotune() { 
	wavesurferAutotuned.load("/score_recording");
	autotuned_audio = true;
	$( "#wsAPlay" ).prepend("<button class=\"btn btn-primary wavesurferPlay\" id=\"wsAPlayBtn\" onclick=\"wavesurferAutotuned.playPause()\"><i id=\"tmpLoad\" class=\"fa fa-circle-o-notch fa-spin\"></i></button>");
	wavesurferAutotuned.on('ready', function () {
	    $("#wsAPlayBtn").append("<i class=\"glyphicon glyphicon-play\"></i>");
	    $("#tmpLoad").attr('class', 'glyphicon glyphicon-edit');
	    $.ajax({
		  type: "GET",
		  url: "/score",
		  data: "",
		}).done(function(data) {
			$( "#score" ).text( "Score: " + data );
		});
		$.ajax({
		  type: "GET",
		  url: "/get_pitches",
		  data: "",
		}).done(function(data) {
			autotuneConfig = {
	            label: "your voice",
	            borderColor: 'rgb(102, 0, 102)',
	            fill: false,
	            data: data,
	            steppedLine: true
	        };
			chart.data.datasets.push(autotuneConfig);
			chart.update();
		});
	});
}

function playExercise() { 
	var times = current_level[current_exercise_num].times;
	var freqs = current_level[current_exercise_num].freqs;
	if (!autotuned_audio) { drawPitchChart(freqs, times); }
	var oscillator = audio_context.createOscillator();
	oscillator.type = 'sine';
	var total_duration = 0
    oscillator.connect(analyzer);
    setTimeout(function() { 
		metronome.play();
	 }, 1000);
	setTimeout(function() { 
		metronome.play();
	 }, 2000);
	setTimeout(function() { 
		metronome.play()
	 }, 3000);
    for (i=0; i<freqs.length; i++) { 
    	oscillator.frequency.setValueAtTime(freqs[i], audio_context.currentTime + total_duration + 4.3);
    	total_duration += times[i];
    };
    setTimeout(function() { oscillator.start(); }, 4300);
    setTimeout(
        function(){
            oscillator.stop();
            oscillator.disconnect(analyzer);
            $('#record-btn').prop('disabled', false);
    }, 4300 + total_duration*1000);
}

function loadExercises(level) { 
	current_level = EXERCISES[level-1]; // Load exercises
	current_exercise_num = 0; // Start counter for current exercise
	var exercise = current_level[current_exercise_num];
	$( "#exercise" ).text( exercise.text );
	$( "#score" ).text( "Score: 0" );
}

function completeExercise() { 
	// Update progress bar
	current_exercise_num += 1;
	var width =String(100*(current_exercise_num)/current_level.length);
	$("#progress").css("width",  width+"%");
	$("#progress").text(Math.floor(width) + "% complete");
	exercise_complete_snd.play();
	resetCanvas();
	if (current_exercise_num == current_level.length) {
	    setTimeout(
	        function(){
	            $('#complete-level').modal('show');
	    }, 1000); 
	} else { 
		clearAudio();
		var exercise = current_level[current_exercise_num];
		$( "#exercise" ).text( exercise.text )
	}
}

function completeLevel(level) {
	// Reset buttons
	clearAudio()
	level_complete_snd.play();
	$("#progress").css("width", "0%");
	// Clear out saved audio
	if (level==NUM_LEVELS) { 
		console.log("TODO"); // Figure out what to do if finished all levels
	} else { 
		current_level = EXERCISES[level]; // Load exercises
		current_exercise_num = 0; // Start counter for current exercise
		$( "#level" ).text( LEVEL_TEXT_MAP[level] );
		$( "#exercise" ).text( current_level[current_exercise_num].text );
	}
}

function clearAudio() { 
	$('#record-btn').prop('disabled', true);
	$('#ok-btn').prop('disabled', true);
	$('#autotune-btn').prop('disabled', true);
	recorded_audio = null;
	autotuned_audio = null; 
	$("#wavesurferRecorded").empty();
	$("#wavesurferAutotuned").empty();
	$("#wsRPlay").empty();
	$("#wsAPlay").empty();
	wavesurferRecorded = WaveSurfer.create({
	    container: '#wavesurferRecorded',
	    waveColor: 'purple',
	    progressColor: 'violet',
	    barHeight: 2, 
	    barWidth: 2, 
	    hideScrollbar: true,
	    cursorColor: "silver"
	});
	wavesurferAutotuned = WaveSurfer.create({
	    container: '#wavesurferAutotuned',
	    waveColor: 'orange',
	    progressColor: 'coral', 
	    barHeight: 2,
	    barWidth: 2, 
	    hideScrollbar: true, 
	    cursorColor: "silver"
	});
};

function startRecordingOnTimer() { 
	setTimeout(function() { 
		$("#recordingCue").text( "Recording in 3...");
		metronome.play();
	 }, 1000);
	setTimeout(function() { 
		$("#recordingCue").text( "Recording in 2...");
		metronome.play();
	 }, 2000);
	setTimeout(function() { 
		$("#recordingCue").text( "Recording in 1...");
		metronome.play()
	 }, 3000);
	setTimeout(startRecording, 4000);
}

function signIn() { 
	// Crappy JS, here just because hacky solution was quicker
	// Either text is on Next (go to instructions), or Submit (enter app)
	if ($("#signin-btn").text() == "Next") { 
		username = $( "#userName" ).val();
		var level = $("#level-select").find("option:selected").text();
		if (username != "") { 
			audio_context = new AudioContext();
			analyzer = audio_context.createAnalyser();
			analyzer.connect(audio_context.destination);
			initializeAudio();
			$("#user").html("Welcome, " + "<strong>" + username + "</strong>");
			$("#level").text(level);
			var levelNum = parseInt(level[6]);
			loadExercises(levelNum);	
			$("#select-menu").empty();
			$("#signin-btn").text("Login");
			$("#instructions").show();
		};
	} else { 
		$('#signin').modal('hide');	
	}

}

function initializeAudio() { 
    // Access the Microphone using the navigator.getUserMedia method to obtain a stream
    navigator.getUserMedia({ audio: true }, function (stream) {
        // Expose the stream to be accessible globally
        audio_stream = stream;
        // Create the MediaStreamSource for the Recorder library
        var input = audio_context.createMediaStreamSource(stream);
        meter = createAudioMeter(audio_context);
        drawLoop();
    	input.connect(meter);
        console.log('Media stream succesfully created');

        // Initialize the Recorder Library
        recorder = new Recorder(input);
        console.log('Recorder initialised');

    }, function (e) {
        console.error('No live audio input: ' + e);
    });
}


function drawLoop( time ) {
	gauge.set(meter.volume*140);
    rafID = window.requestAnimationFrame( drawLoop );
}




