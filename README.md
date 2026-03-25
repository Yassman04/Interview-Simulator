# Interview Simulator 🎙️

A fully interactive, web-based interview simulator powered by advanced AI and computer vision. This application streams live audio, generates human-like vocal responses, evaluates transcript answers, and analyzes physical body language in real time to provide comprehensive interview feedback.

## Features
* **Dynamic AI Interviewer:** Generates custom interview questions based on the selected job role.
* **Live Audio Processing:** Uses microphone capture and cloud transcription to process spoken answers.
* **Real-Time Body Language Monitor:** Utilizes MediaPipe Holistic to track facial visibility and hand gestures silently in the background.
* **Comprehensive Feedback:** Evaluates both spoken content and physical presentation, delivering a detailed HTML grading report.

## Examiner Setup Instructions

**Important Note Regarding API Keys:** For ease of grading, the required `.env` file containing active API keys has been intentionally included in this directory. You do not need to supply your own keys to test this application. 

### 1. Install Dependencies
Open your terminal in this project folder and install the required Python packages:
`pip install -r requirements.txt`

### 2. Run the Server
Start the Flask application by running:
`python app.py`

### 3. Open the Application
The application should automatically launch in your default web browser. If it does not, manually navigate to:
`http://127.0.0.1:5000/`

## Usage
1. Enter a target job role and the number of questions you wish to answer.
2. Select your preferred interviewer voice from the settings menu.
3. Use the **Click to Speak** button to record your answers. 
4. Click **Finish Interview** to generate your final evaluation.