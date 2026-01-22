import sounddevice as sd
from scipy.io.wavfile import write
import asyncio
from backend.speech_to_text import process_voice_entry, record_audio


audio_file = "data/audio/test_diary.wav"

record_audio(audio_file, duration=10) 

# Transkribera, LLM tar ut variablerna, sparar i .csv 
asyncio.run(process_voice_entry(audio_file))