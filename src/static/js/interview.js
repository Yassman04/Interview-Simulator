// --- Settings Menu Logic ---
const settingsBtn = document.getElementById('settings-btn');
const settingsMenu = document.getElementById('settings-menu');

settingsBtn.addEventListener('click', () => {
    settingsMenu.classList.toggle('show');
});

document.addEventListener('click', (event) => {
    if (!settingsBtn.contains(event.target) && !settingsMenu.contains(event.target)) {
        settingsMenu.classList.remove('show');
    }
});

let selectedVoiceModel = "aura-asteria-en";
const voiceRadios = document.querySelectorAll('input[name="voice_select"]');

// FIX 1: This is the corrected voice radio section
voiceRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        selectedVoiceModel = e.target.value;
        window.INITIAL_AUDIO_DATA = null; // Destroys the hoarded audio when you click a new voice!
    });
});

// --- Voice Toggle Logic ---
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
        
        if (currentAudio) {
            currentAudio.pause();
        }
    }
});

// --- Dynamic Audio Fetching ---
async function playFirstQuestion() {
    if (!isVoiceEnabled) return; 
    
    const firstAudioData = window.INITIAL_AUDIO_DATA; 
    
    if (firstAudioData && firstAudioData !== "None") {
        if (currentAudio) currentAudio.pause();
        currentAudio = new Audio("data:audio/mp3;base64," + firstAudioData);
        currentAudio.play();
        return; // Exit early since we played the initial audio
    }

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

        if (data.audio_base64) {
            if (currentAudio) currentAudio.pause();
            currentAudio = new Audio("data:audio/mp3;base64," + data.audio_base64);
            currentAudio.play();
        }
    } catch (error) {
        console.error("Audio error:", error);
    }

    playBtn.textContent = "🔊 Listen to Question";
    playBtn.disabled = false;
}

// --- MEDIAPIPE HOLISTIC COMPUTER VISION LOGIC ---
const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('output_canvas');
const canvasCtx = canvasElement.getContext('2d');

// digital scorecard
let bodyMetrics = {
    totalFrames: 0,
    faceVisible: 0,
    handsVisible: 0
};

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

holistic.onResults(function(results) {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // This draws the connections on the face and the hands, remove comment to see how it tracks body language
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
    }*/

    canvasCtx.restore();

    // Tally the scorecard ONLY while the user is recording!
    if (isRecording) {
        bodyMetrics.totalFrames++;
        if (results.faceLandmarks) bodyMetrics.faceVisible++;
        if (results.leftHandLandmarks || results.rightHandLandmarks) bodyMetrics.handsVisible++;
    }
});

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await holistic.send({image: videoElement});
    },
    width: 400,
    height: 300
});
camera.start();

// --- MICROPHONE & INTERVIEW LOGIC ---
const recordBtn = document.getElementById('record-btn');
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

recordBtn.addEventListener('click', async () => {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            // Reset the scorecard to zero for the new question!
            bodyMetrics = { totalFrames: 0, faceVisible: 0, handsVisible: 0 };

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                recordBtn.textContent = "Grading Answer...";
                recordBtn.style.backgroundColor = "#f39c12"; 
                recordBtn.disabled = true;

                const formData = new FormData();
                formData.append('audio', audioBlob, 'answer.webm');
                formData.append('voice_model', selectedVoiceModel);
                
                
                formData.append('metrics', JSON.stringify(bodyMetrics));

                fetch('/process_audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    const chatBox = document.getElementById('chat-window');
                    
                    if (data.transcript) {
                        const userMessage = document.createElement('p');
                        userMessage.className = "user-msg";
                        userMessage.innerHTML = `<strong>You:</strong> ${data.transcript}`;
                        chatBox.appendChild(userMessage);
                    }
                    
                    if (data.next_question) {
                        const aiMessage = document.createElement('p');
                        aiMessage.className = "interviewer-msg";
                        aiMessage.innerHTML = `<strong>Interviewer:</strong> ${data.next_question}`;
                        chatBox.appendChild(aiMessage);
                        
                        window.INITIAL_AUDIO_DATA = null; 
                        
                        if (data.audio_base64 && isVoiceEnabled) {
                            if (currentAudio) currentAudio.pause();
                            currentAudio = new Audio("data:audio/mp3;base64," + data.audio_base64);
                            currentAudio.play();
                        }
                    }

                    chatBox.scrollTop = chatBox.scrollHeight;
                    
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
    } else {
        mediaRecorder.stop();
        isRecording = false;
    }
});

// --- Loading State for the Finish Button ---
const finishBtn = document.getElementById('finish-btn');
finishBtn.addEventListener('click', function() {
    this.textContent = "Generating Feedback... ⏳";
    this.style.backgroundColor = "#f39c12"; 
    this.style.pointerEvents = "none"; 
});