from google import genai
from google.genai import types
from config import Interviewer_API_KEY

# Initialize the client
client = genai.Client(api_key=Interviewer_API_KEY)

def generate_questions(job_role, num_of_questions):
    """Generates a batch of interview questions based on the job role."""
    
    chat = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=f"You are a professional interviewer. Generate exactly {num_of_questions} high quality interview questions for the requested position. Separate each question with a vertical bar character (|). Do not include any other text."
        ),
    )

    prompt = f"I am applying for the {job_role} position. Please generate my {num_of_questions} questions."
    
    try:
        response = chat.send_message(prompt)
        # Split the response into a Python list using the vertical bar
        questions_list = [q.strip() for q in response.text.split("|") if q.strip()]
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        questions_list = []

    # Safety check in case the format gets messy or the API fails
    if len(questions_list) < num_of_questions:
        fallback_questions = [
            "Tell me about yourself.",
            "What is your greatest strength?",
            "Describe a challenge you overcame.",
            "Where do you see yourself in 5 years?",
            "Why do you want this role?",
            "What is your greatest weakness?",
            "How do you handle conflict in the workplace?",
            "Describe a time you showed leadership.",
            "Why should we hire you?",
            "Do you have any questions for us?"
        ]
        questions_list = fallback_questions[:num_of_questions]
        
    return questions_list