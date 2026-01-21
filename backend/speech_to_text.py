import pandas as pd
from datetime import datetime
from faster_whisper import WhisperModel
from backend.constants import DATA_PATH
from backend.agents import stt_agent
import locale
import sounddevice as sd
from scipy.io.wavfile import write

# Måste ha detta för att få ut svenska ord för veckodagarna..........
try:
    locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")
except:
    pass # Blir engelska ord i stället

# Whisper Setup - 'tiny' eller 'base' är snabba för CPU. 'small'/'medium' är bättre men kräver mer.
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    segments, _ = whisper_model.transcribe(audio_path, language="sv")
    # Slå ihop alla segment till en sträng
    text = " ".join([segment.text for segment in segments])
    return text.strip()

async def process_voice_entry(audio_path: str):
    print("Transkriberar ljud...")
    raw_text = transcribe_audio(audio_path)
    print(f"   Transkription: '{raw_text}'")

    if not raw_text:
        print("Inget tal uppfattades.")
        return

    print("LLM skapar strukturerad data...")
    # LLM extraherar activity och mood för att spara i CSV
    result = await stt_agent.run(f"Analysera detta dagboksinlägg: {raw_text}")

    # Ta ut tiden, spara formatet för Å-M-D, och ta ut dagen separat
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday_str = now.strftime("%A").capitalize()

    # Spara till CSV
    file_path = DATA_PATH / "dagbok.csv"
    
    new_entry = {
        "date": date_str,
        "weekday": weekday_str,
        "activity": result.output.activity,
        "mood": result.output.mood
    }
    
    # Om filen inte finns, skapa den med headers
    if not file_path.exists():
        df = pd.DataFrame([new_entry])
    else:
        df = pd.read_csv(file_path)
        # Fix för pandas concat varning, fattar inte denna dock... Kan man inte bara adda?
        new_df = pd.DataFrame([new_entry])
        df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    print(f"Sparat i dagboken: {new_entry}")
    
    return new_entry


# Index 26 = Microphone Array.... 
# ENDAST FÖR MIG! Kör list_audio_devices.py för att se eran standard mick
# fs och channels kan behöva ändras beroende på er mick
DEVICE_ID = 26

# rec(), wait(), write() 
def record_audio(filename, duration=10, fs=48000):
    print(f"Spelar in i {duration} sekunder...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, device=DEVICE_ID)
    sd.wait() 
    write(filename, fs, recording) # 
    print("Inspelning klar.")