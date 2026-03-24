from google import genai
from config import Interviewer_API_KEY

# Initialize the client
client = genai.Client(api_key=Interviewer_API_KEY)

def generate_web_feedback(transcript, job_role):
    """Sends the interview transcript to Gemini and requests HTML formatted feedback."""
    
    if not transcript:
        return "<p>No questions were answered during this session.</p>"

    # 1. Format the transcript so it can read it easily
    conversation = ""
    for i, entry in enumerate(transcript, 1):
        conversation += f"<strong>Q{i}:</strong> {entry['q']}<br>"
        conversation += f"<strong>Answer:</strong> {entry['a']}<br><br>"

    # 2. Give strict instructions to act as a hiring manager and return HTML
    prompt = f"""
    You are an expert hiring manager. Review this interview transcript for a {job_role} position.
    
    Transcript:
    {conversation}
    
    Provide constructive feedback on the user's answers. Highlight what they did well and what they can improve.
    Format your entire response using clean HTML. Use <h3> for section headers, <p> for paragraphs, and <ul>/<li> for bullet points.
    Do NOT use Markdown. Do NOT include ```html code blocks. Just return the raw HTML tags.
    """
    
    try:
        print("Generating final feedback...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
        
    except Exception as e:
        print(f"Feedback API Error: {e}")
        return "<p>Sorry, there was an error generating your feedback. Please try again.</p>"