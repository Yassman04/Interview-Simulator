import os
import json
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, session, redirect, url_for

# Custom Modules for AI Integration
from speech_to_text import transcribe_audio_file
from text_to_speech import generate_human_audio
from feedback import generate_web_feedback
from interviewer import generate_questions

# --- FLASK APPLICATION SETUP --- #
app = Flask(__name__)
app.secret_key = "interview_simulator_secret_key"


# --- ROUTE 1: CONFIGURATION & SETUP --- #
@app.route("/", methods=["GET", "POST"])
def setup():
    """
    Handles the landing page. Captures the user's target job role and desired 
    interview length, generates the questions via Gemini, and stores them in the session.
    """
    if request.method == "POST":
        # Extract form data from the UI
        job_role = request.form.get("job_role")
        num_questions = int(request.form.get("num_questions", 5))

        # Store configuration in Flask's encrypted session memory
        session["job_role"] = job_role
        session["num_questions"] = num_questions

        print(f"Generating {num_questions} questions for {job_role}...")
        
        # Pre-generate all interview questions using the Gemini API
        session["questions"] = generate_questions(job_role, num_questions)
        session["current_question_index"] = 0
        session["transcript"] = []  # Initialize empty list to hold Q&A history

        return redirect(url_for("interview"))

    return render_template("setup.html")


# --- ROUTE 2: THE INTERVIEW DASHBOARD --- #
@app.route("/interview")
def interview():
    """
    Renders the main interview interface. Retrieves the first generated question
    and pre-loads the Deepgram audio payload so the UI can render instantly.
    """
    # Security check: Ensure user completed setup before accessing this room
    if "job_role" not in session or "questions" not in session:
        return redirect(url_for("setup"))

    # Retrieve the first question to initialize the UI
    first_question = session["questions"][0]

    # Pre-generate the audio for the first question to minimize latency on page load
    print("Generating audio for the first question...")
    first_audio = generate_human_audio(first_question)

    return render_template(
        "interview.html",
        job_role=session["job_role"],
        first_question=first_question,
        first_audio=first_audio,
    )


# --- ROUTE 3: AUDIO PROCESSING & INTERVIEW LOGIC --- #
@app.route("/process_audio", methods=["POST"])
def process_audio():
    """
    The core logic loop of the application. Receives a user's audio response and
    body language metrics, transcribes the audio via Deepgram, appends the data 
    to the transcript, and returns the next question and its audio payload.
    """
    # 1. Validation & File Handling
    if "audio" not in request.files:
        return {"error": "No file received"}, 400

    audio_file = request.files["audio"]
    save_path = os.path.join("src", "temp_answer.webm")
    audio_file.save(save_path)

    # 2. Transcription 
    transcript = transcribe_audio_file(save_path)

    # 3. Retrieve current state from session memory
    current_index = session.get("current_question_index", 0)
    questions = session.get("questions", [])
    current_question = questions[current_index]

    # 4. Extract Body Language Metrics (Sent from MediaPipe in the browser)
    raw_metrics = request.form.get(
        "metrics", '{"totalFrames": 0, "faceVisible": 0, "handsVisible": 0}'
    )
    metrics = json.loads(raw_metrics)

    # 5. Update the running transcript with Question, Answer, and Metrics
    session["transcript"].append(
        {"q": current_question, "a": transcript, "metrics": metrics}
    )

    # 6. Advance the interview state
    session["current_question_index"] += 1
    session.modified = True
    next_index = session["current_question_index"]

    # 7. Determine Next Steps (Continue or Conclude)
    if next_index < len(questions):
        next_question = questions[next_index]
        is_finished = False
    else:
        next_question = "That concludes our interview! Thank you for your time. Please click 'Finish Interview' to see your final feedback."
        is_finished = True

    # 8. Generate Audio for the next prompt based on user settings
    selected_voice = request.form.get("voice_model", "aura-asteria-en")
    print(f"Generating human voice using {selected_voice}...")
    audio_data = generate_human_audio(next_question, selected_voice)

    # 9. Return structured data to the frontend JavaScript
    return {
        "status": "success",
        "transcript": transcript,
        "next_question": next_question,
        "audio_base64": audio_data,
        "is_finished": is_finished,
    }


# --- ROUTE 4: DYNAMIC AUDIO REGENERATION --- #
@app.route("/get_audio", methods=["POST"])
def get_audio():
    """
    A utility endpoint that allows the frontend to request a new audio file
    if the user changes their voice preference mid-interview.
    """
    data = request.json
    text = data.get("text")
    voice = data.get("voice_model", "aura-asteria-en")

    # Generate fresh audio using the newly selected voice profile
    audio_base64 = generate_human_audio(text, voice)

    return {"audio_base64": audio_base64}


# --- ROUTE 5: THE FINAL EVALUATION --- #
@app.route("/feedback")
def feedback():
    """
    Renders the final results page. Passes the complete transcript (including 
    text and body language data) to Gemini to generate a comprehensive evaluation.
    """
    # Security check: Ensure transcript exists before generating feedback
    if "job_role" not in session or "transcript" not in session:
        return redirect(url_for("setup"))

    job_role = session["job_role"]
    transcript = session["transcript"]

    # Request the final comprehensive grade from the Gemini API
    ai_evaluation = generate_web_feedback(transcript, job_role)

    return render_template("feedback.html", job_role=job_role, evaluation=ai_evaluation)


# --- SERVER STARTUP --- #
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Ensure the browser only opens once, preventing duplicate tabs during auto-reload
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1.0, open_browser).start()
    app.run(debug=True)