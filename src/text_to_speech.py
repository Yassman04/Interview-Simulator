import requests
import base64
from config import API_KEY

# added 'voice_model' as an input, defaulting to asteria just in case!
def generate_human_audio(text, voice_model="aura-asteria-en"):
    """Sends text to Deepgram Aura and returns base64 audio data."""
    
    # The URL now dynamically injects whatever voice the user clicked
    url = f"https://api.deepgram.com/v1/speak?model={voice_model}"
    
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        return audio_base64
        
    except Exception as e:
        print(f"Deepgram TTS Error: {e}")
        return None