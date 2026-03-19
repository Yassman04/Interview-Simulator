from google import genai
from google.genai import types
from speech_to_text import listen_to_user
from config import Interviewer_API_KEY
from feedback import generate_feedback
import time
import sys

# Initialize the client
client = genai.Client(api_key=Interviewer_API_KEY)


def typewriter_print(text, delay=0.03):
    """Prints text one character at a time for a natural conversational feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line when finished


def run_mock_interview():
    print("\n===== AI Interview Simulator =====")

    # 1. Get the Job Position
    job_role = input("Interviewer: What position are you applying for today?\nUser: ")

    # Start the chat session
    chat = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="You are a professional interviewer. Generate exactly five high quality interview questions for the requested position. Separate each question with a vertical bar character (|). Do not include any other text."
        ),
    )

    transcript = []

    # 2. Batch Generate All Questions at Once
    print("\n[System] Generating interview questions, please wait...")
    prompt = (
        f"I am applying for the {job_role} position. Please generate my 5 questions."
    )

    response = chat.send_message(prompt)

    # Split the response into a Python list using the vertical bar
    questions_list = [q.strip() for q in response.text.split("|") if q.strip()]

    # Safety check in case the format gets messy
    if len(questions_list) < 5:
        questions_list = [
            "Tell me about yourself.",
            "What is your greatest strength?",
            "Describe a challenge you overcame.",
            "Where do you see yourself in 5 years?",
            "Why do you want this role?",
        ]

    time.sleep(1)  # Brief pause before the interview starts

    # 3. The Interview Loop (No API calls here!)
    # Updated to loop through all 5 questions
    for i, ai_question in enumerate(questions_list[:5], 1):
        print(f"\n===== Question {i} =====")
        time.sleep(0.5)

        # Use the typewriter effect for the interviewer's voice
        sys.stdout.write("Interviewer: ")
        sys.stdout.flush()
        typewriter_print(ai_question)

        # Trigger speech to text module
        user_answer = listen_to_user()
        print(f"User (Transcribed): {user_answer}")

        # Save to the transcript
        transcript.append({"q": ai_question, "a": user_answer})

        time.sleep(1)  # Natural pause before the next question

    # 4. Final Wrap up
    print("\n===== Interview Complete =====")
    time.sleep(1)
    print("Review your transcript below:")
    for idx, entry in enumerate(transcript, 1):
        print(f"\nQ{idx}: {entry['q']}")
        print(f"A{idx}: {entry['a']}")
        time.sleep(0.5)  # Slight delay while printing the transcript

    # 5. Get Evaluation
    time.sleep(1)
    generate_feedback(client, transcript, job_role)
