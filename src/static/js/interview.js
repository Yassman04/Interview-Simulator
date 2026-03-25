// --- 1. SETTINGS & UI MENU LOGIC --- //

const settingsBtn = document.getElementById('settings-btn');
const settingsMenu = document.getElementById('settings-menu');

// Toggle the voice settings dropdown menu
settingsBtn.addEventListener('click', () => {
    settingsMenu.classList.toggle('show');
});

// Close the settings menu if the user clicks anywhere outside of it
document.addEventListener('click', (event) => {
    if (!settingsBtn.contains(event.target) && !settingsMenu.contains(event.target)) {
        settingsMenu.classList.remove('show');
    }
});


// --- 2. VOICE PREFERENCES & PLAYBACK --- //

let selectedVoiceModel = "aura-asteria-en";
const voiceRadios = document.querySelectorAll('input[name="voice_select"]');

// Listen for changes to the voice selection radio buttons
voiceRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        selectedVoiceModel = e.target.value;
        // Destroy the hoarded audio payload so the app knows to fetch a new 
        // audio file with the newly selected voice model
        window.INITIAL_AUDIO_DATA = null; 
    });
});

// Voice Toggle (Mute/Unmute) Logic
let currentAudio = null;
let isVoiceEnabled = true;
const voiceToggleBtn = document.getElementById('audio-toggle');

voiceToggleBtn.addEventListener('click', () => {
    isVoiceEnabled = !isVoiceEnabled;
    
    if (isVoiceEnabled) {
        voiceToggleBtn.textContent = "🔊 Voice is ON";
        voiceToggleBtn.style.backgroundColor = "#27ae60"; 
    } else {
        voiceToggleBtn.textContent = "🔇 Voice is OFF";
        voiceToggleBtn.style.backgroundColor = "#95a5a6"; 
        
        // Immediately stop speaking if the user mutes mid-sentence
        if (currentAudio) {
            currentAudio.pause();
        }
    }
});

// Dynamic Audio Fetching for the "Listen" Button
async function playFirstQuestion() {
    if (!isVoiceEnabled) return; 
    
    const firstAudioData = window.INITIAL_AUDIO_DATA; 
    
    // Check if we already have the audio pre-loaded from Python
    if (firstAudioData && firstAudioData !== "None") {
        if (currentAudio) currentAudio.pause();
        currentAudio = new Audio("data:audio/mp3;base64," + firstAudioData);
        currentAudio.play();
        return; 
    }

    // If no pre-loaded audio exists, fetch it via API
    const questionText = document.getElementById('current-question').innerText;
    const playBtn = document.querySelector('.play-audio-btn');
    
    playBtn.textContent = "⏳ Loading Voice...";
    playBtn.disabled = true;

    try {
        const response = await fetch('/get_audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: questionText,
                voice_model: selectedVoiceModel
            })
        });

        const data = await response.json();

        // Play the freshly generated audio
        if (data.audio_base64) {
            if (currentAudio) currentAudio.pause();
            currentAudio = new Audio("data:audio/mp3;base64," + data.audio_base64);
            currentAudio.play();
        }
    } catch (error) {
        console.error("Audio error:", error);
    }

    // Reset button state
    playBtn.textContent = "🔊 Listen";
    playBtn.disabled = false;
}


// --- 3. MEDIAPIPE HOLISTIC COMPUTER VISION LOGIC --- //

const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');

// Digital scorecard to track presence and gestures
let bodyMetrics = {
    totalFrames: 0,
    faceVisible: 0,
    handsVisible: 0
};

// Initialize Google MediaPipe Holistic Model
const holistic = new Holistic({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
}});

holistic.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    refineFaceLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});

// Event Listener: Fires every time the camera captures a frame
holistic.onResults(function(results) {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Note: Remove these comments to visually draw the tracking skeleton on the canvas
    /*
    if (results.faceLandmarks) {
        drawConnectors(canvasCtx, results.faceLandmarks, FACEMESH_TESSELATION, {color: '#27ae6050', lineWidth: 1});
        drawConnectors(canvasCtx, results.faceLandmarks, FACEMESH_RIGHT_EYE, {color: '#e74c3c', lineWidth: 2});
        drawConnectors(canvasCtx, results.faceLandmarks, FACEMESH_LEFT_EYE, {color: '#e74c3c', lineWidth: 2});
    }
    
    if (results.leftHandLandmarks) {
        drawConnectors(canvasCtx, results.leftHandLandmarks, HAND_CONNECTIONS, {color: '#3498db', lineWidth: 2});
        drawLandmarks(canvasCtx, results.leftHandLandmarks, {color: '#2980b9', lineWidth: 1, radius: 2});
    }
    
    if (results.rightHandLandmarks) {
        drawConnectors(canvasCtx, results.rightHandLandmarks, HAND_CONNECTIONS, {color: '#f1c40f', lineWidth: 2});
        drawLandmarks(canvasCtx, results.rightHandLandmarks, {color: '#f39c12', lineWidth: 1, radius: 2});
    }
    */

    canvasCtx.restore();

    // Tally the scorecard only while the user is actively recording an answer!
    if (isRecording) {
        bodyMetrics.totalFrames++;
        if (results.faceLandmarks) bodyMetrics.faceVisible++;
        if (results.leftHandLandmarks || results.rightHandLandmarks) bodyMetrics.handsVisible++;
    }
});

// Start the webcam feed and stream it into the MediaPipe model
const camera = new Camera(videoElement, {
    onFrame: async () => {
        await holistic.send({image: videoElement});
    },
    width: 400,
    height: 300
});
camera.start();


// --- 4. MICROPHONE & INTERVIEW PROGRESSION LOGIC --- //

const recordBtn = document.getElementById('record-btn');
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

recordBtn.addEventListener('click', async () => {
    // Cut off the interviewer if they are currently speaking
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    // START RECORDING STATE
    if (!isRecording) {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            // Reset the body language scorecard for this specific question
            bodyMetrics = { totalFrames: 0, faceVisible: 0, handsVisible: 0 };

            // Collect audio data chunks as they are generated
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            // Behavior when recording is stopped
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                recordBtn.textContent = "Grading Answer... ⏳";
                recordBtn.style.backgroundColor = "#f39c12"; 
                recordBtn.disabled = true;

                // Package audio, body language metrics, and voice model into a single payload
                const formData = new FormData();
                formData.append('audio', audioBlob, 'answer.webm');
                formData.append('voice_model', selectedVoiceModel);
                formData.append('metrics', JSON.stringify(bodyMetrics));

                // Send the payload to the Python backend
                fetch('/process_audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    const chatBox = document.getElementById('chat-window');
                    
                    // 1. Append User's transcribed answer to the chat
                    if (data.transcript) {
                        const userMessage = document.createElement('p');
                        userMessage.className = "user-msg";
                        userMessage.innerHTML = `<strong>You:</strong> ${data.transcript}`;
                        chatBox.appendChild(userMessage);
                    }
                    
                    // 2. Append the next question to the chat
                    if (data.next_question) {
                        const aiMessage = document.createElement('p');
                        aiMessage.className = "interviewer-msg";
                        aiMessage.innerHTML = `<strong>Interviewer:</strong> ${data.next_question}`;
                        chatBox.appendChild(aiMessage);
                        
                        // Clear initial audio since we are moving to the next question
                        window.INITIAL_AUDIO_DATA = null; 
                        
                        // Auto-play the next question's audio
                        if (data.audio_base64 && isVoiceEnabled) {
                            if (currentAudio) currentAudio.pause();
                            currentAudio = new Audio("data:audio/mp3;base64," + data.audio_base64);
                            currentAudio.play();
                        }
                    }

                    // Auto-scroll the chat window to the bottom
                    chatBox.scrollTop = chatBox.scrollHeight;
                    
                    // 3. Update the UI state based on interview progress
                    if (data.is_finished) {
                        recordBtn.textContent = "Interview Complete";
                        recordBtn.style.backgroundColor = "#27ae60"; 
                    } else {
                        recordBtn.textContent = "Click to Speak";
                        recordBtn.style.backgroundColor = "#e74c3c"; 
                        recordBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error("Error sending audio:", error);
                    recordBtn.textContent = "Error. Try Again.";
                    recordBtn.disabled = false;
                });

                // Release the microphone stream
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            
            recordBtn.textContent = "Recording... (Click to Stop)";
            recordBtn.style.backgroundColor = "#c0392b"; 

        } catch (err) {
            console.error("Microphone access denied:", err);
            alert("Please allow microphone access to answer questions.");
        }
        
    // STOP RECORDING STATE
    } else {
        mediaRecorder.stop();
        isRecording = false;
    }
});


// --- 5. FINISH INTERVIEW LOADING STATE --- //

const finishBtn = document.getElementById('finish-btn');

finishBtn.addEventListener('click', function() {
    this.textContent = "Generating Feedback... ⏳";
    this.style.backgroundColor = "#f39c12"; 
    // Prevent the user from clicking the button multiple times while Gemini thinks
    this.style.pointerEvents = "none"; 
});