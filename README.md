# Interview Simulator

A full-stack web application designed to help job seekers, students, and professionals prepare for interviews in a realistic, low-latency environment.

Unlike traditional text-based chatbots, this simulator requires users to speak their answers out loud while tracking their non-verbal body language, accurately recreating the cognitive load and pressure of a real face-to-face interview.

## 🚀 Features

- **Dynamic Question Generation:** Utilizes the Gemini API to generate context-aware, role-specific questions on demand, eliminating repetitive static question banks.
- **Low-Latency Voice Interaction:** Integrates Deepgram for high-speed Speech-to-Text (STT) and human-like Text-to-Speech (TTS) audio processing.
- **Real-Time Body Language Tracking:** Leverages Google MediaPipe running client-side to evaluate non-verbal metrics, such as facial presence and hand gestures.
- **Holistic Evaluation Engine:** Provides immediate, actionable feedback on both the verbal content of the answers and physical presentation.

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **APIs & Libraries:** Deepgram API, Google Gemini API, Google MediaPipe Holistic

## 💻 Local Setup Instructions

Follow these steps to run the Interview Simulator locally on your machine.

### 1. Clone the Repository

`git clone https://github.com/Yassman04/Interview-Simulator.git`
`cd Interview-Simulator`

### 2. Install Dependencies

Ensure you have Python 3.8+ installed. It is recommended to use a virtual environment.
`pip install -r requirements.txt`

### 3. Configure Environment Variables (Security)

This project requires external API keys and a Flask secret key to function safely. **Do not hardcode these into your scripts.**

1. Locate the `.env.example` file in the root directory.
2. Rename this file to `.env`.
3. Open the `.env` file and replace the placeholder text with your actual credentials:
   - `DEEPGRAM_API_KEY`: Get this from your Deepgram Console.
   - `GEMINI_API_KEY`: Get this from Google AI Studio.
   - `FLASK_SECRET_KEY`: Generate a random string (e.g., run `python -c "import secrets; print(secrets.token_hex(16))"` in your terminal).

### 4. Run the Application

Start the Flask server:
`python app.py`

The application will automatically open in your default web browser at `http://127.0.0.1:5000/`.

## 🔒 Security Note

The `.env` file is intentionally included in the `.gitignore` to prevent sensitive API keys and session secrets from being committed to version control. Always use the `.env.example` template when setting up a fresh environment.
