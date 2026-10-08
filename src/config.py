import os
from dotenv import load_dotenv

# Find the directory of config.py (the /src folder)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the root project folder
root_dir = os.path.dirname(current_dir)

# Create the full path to the .env file
dotenv_path = os.path.join(root_dir, ".env")

# Load it
load_dotenv(dotenv_path)

# Keys are read using the names documented in .env.example.
# The older names (API_KEY / Interviewer_API_KEY) still work as a fallback.
API_KEY = os.getenv("DEEPGRAM_API_KEY") or os.getenv("API_KEY")  # Deepgram (speech-to-text and text-to-speech)
Interviewer_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("Interviewer_API_KEY")  # Google Gemini (questions and feedback)

if not API_KEY or not Interviewer_API_KEY:
    print("Warning: DEEPGRAM_API_KEY and/or GEMINI_API_KEY are missing. Copy .env.example to .env and add your keys.")