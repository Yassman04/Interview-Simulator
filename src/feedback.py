from google import genai
from config import Interviewer_API_KEY

# Initialize the client
client = genai.Client(api_key=Interviewer_API_KEY)

def generate_web_feedback(transcript, job_role):
    """Sends the transcript and body language metrics to Gemini for a comprehensive evaluation."""
    
    if not transcript:
        return "<p>No questions were answered during this session.</p>"

    # 1. Format the transcript AND check if the camera was actually used
    conversation = ""
    for i, entry in enumerate(transcript, 1):
        q = entry.get('q', 'Unknown Question')
        a = entry.get('a', 'No answer recorded.')
        metrics = entry.get('metrics', {'totalFrames': 0, 'faceVisible': 0, 'handsVisible': 0})
        
        # Check if the camera was on and capturing frames
        total = metrics.get('totalFrames', 0)
        if total > 0:
            face_pct = round((metrics.get('faceVisible', 0) / total) * 100)
            hands_pct = round((metrics.get('handsVisible', 0) / total) * 100)
            body_language_data = f"Face visible/Eye contact maintained {face_pct}% of the time. Hand gestures used {hands_pct}% of the time."
        else:
            
            body_language_data = "No camera feed was detected. The user declined camera access or does not have a webcam. Do NOT evaluate or penalize body language for this question."
            
        conversation += f"<strong>Q{i}:</strong> {q}<br>"
        conversation += f"<strong>Answer:</strong> {a}<br>"
        conversation += f"<em>[System Data: {body_language_data}]</em><br><br>"

    # 2. Give Gemini strict instructions to grade both spoken words and physical presence
    prompt = f"""
    You are an expert hiring manager. Review this interview transcript for a {job_role} position.
    
    Here is the candidate's performance data:
    {conversation}
    
    Provide comprehensive, constructive feedback on the user's performance. 
    You MUST evaluate TWO specific areas:
    1. Spoken Content: The quality of their verbal answers, clarity, and relevance to the {job_role} role.
    2. Body Language: Their physical presence based on the system data provided. Note that 0% hand usage means they were completely stiff, 15-40% is a healthy amount of natural conversational gesturing, and anything over 80% is dangerously frantic.
    3. Do not add a signature at the bottom of the page like a letter

    Format your entire response using clean HTML. Use <h3> for section headers, <p> for paragraphs, and <ul>/<li> for bullet points.
    Do NOT use Markdown. Do NOT include ```html code blocks. Just return the raw HTML tags.
    """
    
    try:
        print("Generating final feedback including body language analysis...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
        
    except Exception as e:
        print(f"Feedback API Error: {e}")
        return "<p>Sorry, there was an error generating your feedback. Please try again.</p>"