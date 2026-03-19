def generate_feedback(client, transcript, job_role):
    print("\n===== Generating Feedback =====")
    
    
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
    
    Please provide constructive feedback for the candidate. Highlight what they did well, point out areas for improvement, and give specific advice on how they can give stronger answers next time.
    
    FORMATTING RULES:
    1. DO NOT use any Markdown formatting whatsoever. No asterisks, no bolding, no italics.
    2. Use plain text only.
    3. Use ALL CAPS for section headers to make them stand out.
    
    Please structure your response exactly like this templaten including the gaps between answers:
    ======[THE QUESTION BEING ANSWERED] ======

    QUESTION 1: [Insert Question Here]

      ISSUE: [Briefly state the issue]

      ADVICE: [Give actionable advice]

      EXAMPLE: [Provide a concrete example of a better answer]
      
    (Repeat this structure for all questions)
    
    FINAL ENCOURAGEMENT:
    [Provide a short encouraging closing statement]
    """
    
    # Generate the feedback using the new SDK 
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=evaluation_prompt
    )
    
    print("\n===== Performance Review =====")
    print(response.text)