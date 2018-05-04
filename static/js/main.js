var RECORDING = false;
var audio_context = new AudioContext();
var current_level;
var current_exercise_num;
var recorded_audio;
var autotuned_audio;
var username;
var level;
var NUM_LEVELS = 3;

$( document ).ready(function() {
    console.log( "ready!" );
    $('#record-btn').prop('disabled', true);
	$('#playback-btn').prop('disabled', true);
	$('#autotune-btn').prop('disabled', true);
    $('#signin').modal({backdrop: 'static', keyboard: false})
    $('#complete-level').modal({backdrop: 'static', keyboard: false})
    $('#complete-level').modal('hide');
    $( "#record-btn" ).click(function() {
	  if (RECORDING) { 
	  	stopRecording();
	  	$(this).removeClass("btn btn-danger").addClass("btn btn-primary"); 
	  	$('#autotune-btn').prop('disabled', false);
	  }
	  else { 
	  	startRecording();
	  	$(this).removeClass("btn btn-primary").addClass("btn btn-danger"); 
	  }
	});
	$( "#autotune-btn" ).click(function() { 
		if (autotuned_audio) { autotuned_audio.play(); }
		else if (recorded_audio) { 
			getAutotune(); 
			$('#playback-btn').prop('disabled', false);
		}
	});
	$( "#playback-btn" ).click(function() { 
		if (recorded_audio) { recorded_audio.play(); }
		completeExercise();
	});
	$( "#play-btn" ).click(function() { 
		playExercise();
		$('#record-btn').prop('disabled', false);
	});
	$( "#signin-btn" ).click(function() { 
		username = $( "#userName" ).val();
		var level = $("#level-select").find("option:selected").text();
		if (username != "") { 
			$("#user").html("Welcome, " + "<strong>" + username + "</strong>");
			$("#level").text(level);
			var levelNum = parseInt(level[6]);
			loadExercises(levelNum);
			$('#signin').modal('hide');	
		};
	});
	$( "#complete-level-btn" ).click(function() { 
		var cur_level_num = current_level[0].level
		completeLevel(cur_level_num);
		$('#complete-level').modal('hide');
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
	console.log("STARTING")
	RECORDING = true;
	autotuned_audio = null;
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
            recorded_audio.crossOrigin="anonymous";
            sendRecording(blob);
            recorder.clear();
        }, "audio/wav");
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
	$.ajax({
	  type: "GET",
	  url: "/score_recording",
	  data: "", // TODO: Change based on exercise
	}).done(function(data) {
		var reader = new FileReader();
		var blobData = new Blob([data], { type: 'audio/wav' });
		dataUrl = URL.createObjectURL(blobData);
		autotuned_audio = new Audio("http://127.0.0.1:5000/score_recording");
		autotuned_audio.crossOrigin="anonymous";
		$.ajax({
		  type: "GET",
		  url: "/score",
		  data: "",
		}).done(function(data) {
			$( "#score" ).text( "Score: " + data );
		});
		autotuned_audio.play();
	});
}

function playExercise() { 
	var times = current_level[current_exercise_num].times;
	var freqs = current_level[current_exercise_num].freqs;
	var oscillator = audio_context.createOscillator();
	oscillator.type = 'sine';
	var total_duration = 0
    oscillator.connect(audio_context.destination);
    for (i=0; i<freqs.length; i++) { 
    	oscillator.frequency.setValueAtTime(freqs[i], audio_context.currentTime + total_duration);
    	total_duration += times[i];
    };
    oscillator.start();
    setTimeout(
        function(){
            oscillator.stop();
            oscillator.disconnect(audio_context.destination);
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
		// Reset buttons
		$('#record-btn').prop('disabled', true);
		$('#playback-btn').prop('disabled', true);
		$('#autotune-btn').prop('disabled', true);

		// Clear out saved audio
		recorded_audio = null;
		autotuned_audio = null;
		// Load new prompt
		var exercise = current_level[current_exercise_num];
		$( "#exercise" ).text( exercise.text )
	}
}

function completeLevel(level) {
	// Reset buttons
	$('#record-btn').prop('disabled', true);
	$('#playback-btn').prop('disabled', true);
	$('#autotune-btn').prop('disabled', true);
	$("#progress").css("width", "0%");
	// Clear out saved audio
	recorded_audio = null;
	autotuned_audio = null; 
	if (level==NUM_LEVELS) { 
		console.log("TODO"); // Figure out what to do if finished all levels
	} else { 
		current_level = EXERCISES[level]; // Load exercises
		current_exercise_num = 0; // Start counter for current exercise
		$( "#exercise" ).text( current_level[current_exercise_num].text );
	}
}






