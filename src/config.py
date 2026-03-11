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

API_KEY = os.getenv("API_KEY")