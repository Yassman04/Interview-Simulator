import requests
from config import API_KEY

def transcribe_audio_file(file_path):
    """Sends a saved audio file to Deepgram and returns the text."""
    
    # We use the standard REST API instead of the streaming websocket
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
    
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "audio/webm"
    }
    
    try:
        # Open the webm file and send it to Deepgram
        with open(file_path, "rb") as audio_file:
            response = requests.post(url, headers=headers, data=audio_file)
            
        response.raise_for_status()
        data = response.json()
        
        # Dig into the Deepgram response to grab the exact words
        transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
        
    except Exception as e:
        print(f"Deepgram Error: {e}")
        return "Error transcribing audio."