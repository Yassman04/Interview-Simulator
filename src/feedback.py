# src/feedback.py

def generate_feedback(client, transcript, job_role):
    print("\n--- Generating Feedback ---")
    
    
    # Format the transcript into a readable string
    transcript_text = ""
    for idx, entry in enumerate(transcript, 1):
        transcript_text += f"Q{idx}: {entry['q']}\nA{idx}: {entry['a']}\n\n"
        
    # Create the prompt asking the to grade the interview
    evaluation_prompt = f"""
    You are an expert career coach. 
    A candidate just completed a mock interview for the {job_role} position. 
    Here is the full transcript:
    
    {transcript_text}
    
    Please provide constructive feedback for the candidate. Highlight what they did well, point out areas for improvement, and give specific advice on how they can give stronger answers next time. Keep it professional, concise, and encouraging.
    """
    
    # Generate the feedback using the new SDK (we use models.generate_content for a one-off prompt)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=evaluation_prompt
    )
    
    print("\n--- Performance Review ---")
    print(response.text)