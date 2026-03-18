from google import genai
from google.genai import types
from google.genai import errors
from speech_to_text import listen_to_user
from config import Interviewer_API_KEY
from feedback import generate_feedback
import time
import re

"""NOTES FOR FUTURE:
1. FIX THE HIGH SERVER ACCESS RATE
2. FIX THE COOLDOWN FROM ERROR 429
3. ADD THESE FUNCTIONS TO MAIN.PY
"""

# Initialize the client
client = genai.Client(api_key=Interviewer_API_KEY)


def run_mock_interview():
    print("\n----- AI Interview Simulator -----")

    # 1. Get the Job Position
    job_role = input("Interviewer: What position are you applying for today?\nUser: ")

    # Start the chat session
    chat = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="You are a professional interviewer. Ask one concise, high-quality interview question at a time. Do not provide feedback yet, just ask the question."
        ),
    )

    transcript = []
    user_answer = ""

    # 2. The 3-Question Loop
    for i in range(1, 4):
        print(f"\n----- Question {i} -----")

        if i == 1:
            prompt = f"I am applying for the {job_role} position. I am ready. Please ask the first interview question."
        else:
            prompt = f"My answer to the previous question was: '{user_answer}'. Please ask the next interview question."

        # Get the question with an Exponential Backoff safety net
        retry_count = 0
        while True:
            try:
                response = chat.send_message(prompt)
                break  # If successful, exit the safety loop
            except errors.ClientError as e:
                if e.code == 429:
                    retry_count += 1

                    # Extract the time from the error text
                    match = re.search(r"retry in ([\d\.]+)s", str(e))
                    extracted_time = int(float(match.group(1))) + 1 if match else 15

                    # THE FIX: Force a minimum wait time that grows with each failure
                    # Example: 1st fail = 15s, 2nd fail = 30s, 3rd fail = 45s
                    wait_time = max(extracted_time, 15 * retry_count)

                    print(f"\n[System] Quota limit reached (Attempt {retry_count}).")

                    # Run a live countdown timer
                    for remaining in range(wait_time, 0, -1):
                        # The extra spaces ensure the line overwrites cleanly
                        print(f"Resuming in: {remaining} seconds...    ", end="\r")
                        time.sleep(1)

                    print("\n[System] Cooldown complete, resuming interview...        ")
                else:
                    # If it is a different type of error, let the program crash normally
                    raise e

        ai_question = response.text.strip()
        print(f"\nInterviewer: {ai_question}")

        # Trigger speech-to-text module
        user_answer = listen_to_user()
        print(f"User (Transcribed): {user_answer}")

        # Save to the transcript
        transcript.append({"q": ai_question, "a": user_answer})

    # 3. Final Wrap-up
    print("\n--- Interview Complete ---")
    print("Review your transcript below:")
    for idx, entry in enumerate(transcript, 1):
        print(f"\nQ{idx}: {entry['q']}")
        print(f"A{idx}: {entry['a']}")

    # 4. Get Evaluation
    # Pass the client, the transcript, and the job role over to the other file
    generate_feedback(client, transcript, job_role)


if __name__ == "__main__":
    run_mock_interview()
