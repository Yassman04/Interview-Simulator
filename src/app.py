from flask import Flask, render_template, request, session, redirect, url_for
from speech_to_text import transcribe_audio_file
from text_to_speech import generate_human_audio
from feedback import generate_web_feedback
from interviewer import generate_questions
from threading import Timer
import webbrowser
import os

app = Flask(__name__)
app.secret_key = "interview_simulator_secret_key"


# 1. The Setup / Login Page
@app.route("/", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        job_role = request.form.get("job_role")
        num_questions = int(request.form.get("num_questions", 5))

        session["job_role"] = job_role
        session["num_questions"] = num_questions

        print(f"Generating {num_questions} questions for {job_role}...")
        # Generate all questions immediately and save them to the session memory
        session["questions"] = generate_questions(job_role, num_questions)
        session["current_question_index"] = 0
        session["transcript"] = []  # This will hold the final Q&A for feedback

        return redirect(url_for("interview"))

    return render_template("setup.html")


# 2. The Main Interview Room
@app.route("/interview")
def interview():
    if "job_role" not in session or "questions" not in session:
        return redirect(url_for("setup"))

    # Grab the very first question to display when the page loads
    first_question = session["questions"][0]

    # --- NEW: Generate human audio for the very first question! ---
    print("Generating audio for the first question...")
    first_audio = generate_human_audio(first_question)

    return render_template(
        "interview.html",
        job_role=session["job_role"],
        first_question=first_question,
        first_audio=first_audio,
    )  # Pass it to HTML


# 3. Processing the Audio and Progressing the Interview
@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return {"error": "No file received"}, 400

    audio_file = request.files["audio"]
    save_path = os.path.join("src", "temp_answer.webm")
    audio_file.save(save_path)

    # 1. Transcribe the audio
    transcript = transcribe_audio_file(save_path)

    current_index = session.get("current_question_index", 0)
    questions = session.get("questions", [])

    # 2. Save the question and answer pair to the transcript
    if current_index < len(questions):
        session["transcript"].append({"q": questions[current_index], "a": transcript})
        session["current_question_index"] += 1
        session.modified = True  # Tells Flask to safely update the memory

    # 3. Figure out what the next question is
    next_index = session["current_question_index"]
    if next_index < len(questions):
        next_question = questions[next_index]
        is_finished = False
    else:
        next_question = "That concludes our interview! Thank you for your time. Please click 'Finish Interview' to see your final feedback."
        is_finished = True

    # --- NEW: Catch the voice selection from the web browser! ---
    selected_voice = request.form.get("voice_model", "aura-asteria-en")

    print(f"Generating human voice using {selected_voice}...")
    audio_data = generate_human_audio(next_question, selected_voice)

    # 4. Send everything back to the webpage!
    return {
        "status": "success",
        "transcript": transcript,
        "next_question": next_question,
        "audio_base64": audio_data,
        "is_finished": is_finished,
    }


@app.route("/get_audio", methods=["POST"])
def get_audio():
    # Catch the JSON data sent from the web browser
    data = request.json
    text = data.get("text")
    voice = data.get("voice_model", "aura-asteria-en")

    # Generate the new audio using the requested voice
    audio_base64 = generate_human_audio(text, voice)

    return {"audio_base64": audio_base64}


# 4. The Final Feedback Page
@app.route("/feedback")
def feedback():
    if "job_role" not in session or "transcript" not in session:
        return redirect(url_for("setup"))

    job_role = session["job_role"]
    transcript = session["transcript"]

    # Pass the saved transcript to Gemini to get the HTML grade
    ai_evaluation = generate_web_feedback(transcript, job_role)

    # Send that evaluation to the feedback.html template
    return render_template("feedback.html", job_role=job_role, evaluation=ai_evaluation)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1.0, open_browser).start()
    app.run(debug=True)
