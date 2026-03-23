from flask import Flask, render_template, request, session, redirect, url_for
from speech_to_text import transcribe_audio_file
import webbrowser
from threading import Timer
import os

# We will import your interviewer and feedback logic here very soon!

app = Flask(__name__)
# A secret key is required to use 'session' to remember the job role across pages
app.secret_key = "interview_simulator_secret_key"


# 1. The Setup / Login Page
@app.route("/", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        # When the user submits the form, save their choices and send them to the interview
        session["job_role"] = request.form.get("job_role")
        session["num_questions"] = int(request.form.get("num_questions", 5))
        return redirect(url_for("interview"))

    return render_template("setup.html")


# 2. The Main Interview Room
@app.route("/interview")
def interview():
    # If they try to skip the setup, kick them back to the start
    if "job_role" not in session:
        return redirect(url_for("setup"))

    return render_template("interview.html", job_role=session["job_role"])


# 3. The Final Feedback Page
@app.route("/feedback")
def feedback():
    if "job_role" not in session:
        return redirect(url_for("setup"))

    return render_template("feedback.html")


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return {"error": "No file received"}, 400

    audio_file = request.files["audio"]
    save_path = os.path.join("src", "temp_answer.webm")
    audio_file.save(save_path)

    print(f"Audio saved. Sending to Deepgram...")

    # Pass the saved file to your new Deepgram function
    transcript = transcribe_audio_file(save_path)

    print(f"User said: {transcript}")

    # Send the transcribed text back to the web browser!
    return {"status": "success", "transcript": transcript}


if __name__ == "__main__":
    # This prevents the browser from opening twice when the development server reloads
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1.0, open_browser).start()

    app.run(debug=True)
