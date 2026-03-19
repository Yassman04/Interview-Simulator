import json
import threading
import pyaudio
from websockets.sync.client import connect
from config import API_KEY

def listen_to_user():
    audio = pyaudio.PyAudio()
    device_info = audio.get_default_input_device_info()
    native_rate = int(device_info['defaultSampleRate'])
    
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=native_rate,
        input=True,
        frames_per_buffer=4096
    )

    URL = (
        f"wss://api.deepgram.com/v1/listen"
        f"?model=nova-2"
        f"&encoding=linear16"
        f"&sample_rate={native_rate}"
        f"&channels=1"
        f"&smart_format=true"
    )

    headers = {"Authorization": f"Token {API_KEY}"}
    
    full_answer = ""
    is_recording = True

    print("\n===== ANSWERING =====")

    with connect(URL, additional_headers=headers) as ws:
        
        def receive_transcripts():
            nonlocal full_answer
            try:
                for message in ws:
                    result = json.loads(message)
                    if 'channel' in result:
                        transcript = result['channel']['alternatives'][0]['transcript']
                        if transcript and result.get('is_final'):
                            full_answer += transcript + " "
            except Exception:
                pass

        def send_audio():
            try:
                while is_recording:
                    data = stream.read(4096, exception_on_overflow=False)
                    if data:
                        ws.send(data)
            except Exception:
                pass

        receiver_thread = threading.Thread(target=receive_transcripts)
        sender_thread = threading.Thread(target=send_audio)
        
        receiver_thread.start()
        sender_thread.start()

        input("Press ENTER when you are finished answering\n")
        
        is_recording = False 
        sender_thread.join()

        # Finalize the stream to capture remaining buffer
        ws.send(json.dumps({"type": "CloseStream"}))
        receiver_thread.join()

    stream.stop_stream()
    stream.close()
    audio.terminate()
            
    return full_answer.strip()

