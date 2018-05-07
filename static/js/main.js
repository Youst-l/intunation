var RECORDING = false;
var audio_context;
var analyzer;
var current_level;
var current_exercise_num;
var recorded_audio;
var autotuned_audio;
var username;
var level;
var wavesurferRecorded;
var wavesurferAutotuned
var NUM_LEVELS = 3;

$( document ).ready(function() {
    console.log( "ready!" );
    clearAudio();
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
		var cur_level_num = current_level[0].level
		completeLevel(cur_level_num);
		$('#complete-level').modal('hide');
	});
	$( ".wavesurferPlay" ).click(function() { 
		$(this).find('i').toggleClass('glyphicon glyphicon-arrow-pause').toggleClass('glyphicon glyphicon-arrow-play');
	});
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
    // Access the Microphone using the navigator.getUserMedia method to obtain a stream
    navigator.getUserMedia({ audio: true }, function (stream) {
        // Expose the stream to be accessible globally
        audio_stream = stream;
        // Create the MediaStreamSource for the Recorder library
        var input = audio_context.createMediaStreamSource(stream);
        console.log('Media stream succesfully created');

        // Initialize the Recorder Library
        recorder = new Recorder(input);
        console.log('Recorder initialised');

        // Start recording !
        recorder && recorder.record();
        console.log('Recording...');

    }, function (e) {
        console.error('No live audio input: ' + e);
    });
    var sum = current_level[current_exercise_num].times.reduce(function (accumulator, currentValue) {
	  		return accumulator + currentValue;
		}, 0);
    console.log(sum);
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
    audio_stream.getAudioTracks()[0].stop();
    recorder && recorder.exportWAV(function (blob) {
            var audioUrl = URL.createObjectURL(blob);
            recorded_audio = new Audio(audioUrl);
			wavesurferRecorded.loadBlob(blob);
			$( "#wsRPlay" ).prepend("<button class=\"btn btn-primary wavesurferPlay\" onclick=\"wavesurferRecorded.playPause()\">Original<i class=\"glyphicon glyphicon-play\"></i></button>");
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
	wavesurferAutotuned.load("http://127.0.0.1:5000/score_recording");
	$( "#wsAPlay" ).prepend("<button class=\"btn btn-primary wavesurferPlay\" onclick=\"wavesurferAutotuned.playPause()\">Autotune<i class=\"glyphicon glyphicon-play\"></i></button>");
	$.ajax({
	  type: "GET",
	  url: "/score",
	  data: "",
	}).done(function(data) {
		$( "#score" ).text( "Score: " + data );
	});
}

function playExercise() { 
	var times = current_level[current_exercise_num].times;
	var freqs = current_level[current_exercise_num].freqs;
	var oscillator = audio_context.createOscillator();
	oscillator.type = 'sine';
	var total_duration = 0
    oscillator.connect(analyzer);
    for (i=0; i<freqs.length; i++) { 
    	oscillator.frequency.setValueAtTime(freqs[i], audio_context.currentTime + total_duration);
    	total_duration += times[i];
    };
    oscillator.start();
    setTimeout(
        function(){
            oscillator.stop();
            oscillator.disconnect(analyzer);
            $('#record-btn').prop('disabled', false);
    }, total_duration*1000);
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
	$("#progress").css("width", String(100*(current_exercise_num + 1)/current_level.length) + "%");
	current_exercise_num += 1;
	if (current_exercise_num == current_level.length) {
	    setTimeout(
	        function(){
	            $('#complete-level').modal('show');
	    }, 1000); 
	} else { 
		clearAudio();
		// Load new prompt
		var exercise = current_level[current_exercise_num];
		$( "#exercise" ).text( exercise.text )
	}
}

function completeLevel(level) {
	// Reset buttons
	clearAudio()
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
	    hideScrollbar: true
	});
	wavesurferAutotuned = WaveSurfer.create({
	    container: '#wavesurferAutotuned',
	    waveColor: 'orange',
	    progressColor: 'coral', 
	    barHeight: 2,
	    barWidth: 2, 
	    hideScrollbar: true
	});
};

function startRecordingOnTimer() { 
	setTimeout(function() { $("#recordingCue").text( "Recording in 3...") }, 1000);
	setTimeout(function() { $("#recordingCue").text( "Recording in 2...") }, 2000);
	setTimeout(function() { $("#recordingCue").text( "Recording in 1...") }, 3000);
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





