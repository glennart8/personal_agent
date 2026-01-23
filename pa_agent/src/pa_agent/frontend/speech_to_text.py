from faster_whisper import WhisperModel
import sounddevice as sd
from scipy.io.wavfile import write
import os 
import sys 
import contextlib

whisper_model = WhisperModel("base", device="cpu", compute_type="int8")


def get_devices(type: str = "input") -> dict:
    device_info = sd.query_devices(kind=type)
    
    return device_info

def transcribe_audio(audio_path: str) -> str:
    segments, _ = whisper_model.transcribe(audio_path, language="sv")
    # Slå ihop alla segment till en sträng
    text = " ".join([segment.text for segment in segments])
    
    return text.strip()

def record_audio(filename, samplerate, device, channels, duration=5):
    with open(os.devnull, "w") as devnull:
        with contextlib.redirect_stderr(devnull):
            recording = sd.rec(int(duration*samplerate), samplerate=samplerate, channels=channels, device=device)
            print("Recording...")
            sd.wait()
            print("Recording finnished")
            
    write(filename, samplerate, recording)
    
    return transcribe_audio(filename)
    # return recording

async def ask_db_with_voice(duration=7):
    temp_file = f"{DATA_PATH}/audio/voice_query.wav"
    
    record_audio(temp_file, duration=duration)
    
    print("Transkriberar fråga...")
    query_text = transcribe_audio(temp_file)
    print(f"Transkriberad text: '{query_text}'")
    
    if not query_text:
        print("Ingen fråga uppfattades.")
        return None

    print("Söker i databasen...")
    result = await diary_agent.run(query_text)
    
    return result.output