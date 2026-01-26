from fastapi import FastAPI, UploadFile, File, Response
from rag_agent import diary_agent, science_agent
from stt_agents import stt_agent
from data_models import Prompt
from datetime import datetime
import locale
from data_ingestion import add_data
import io
from speech_to_text import transcribe_audio
import edge_tts
from faster_whisper import WhisperModel
from constants import DATA_PATH
import pandas as pd

# from text_to_speech import 

# Måste ha detta för att få ut svenska ord för veckodagarna..........
try:
    locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")
except:
    pass # Blir engelska ord i stället

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Health check"}

@app.get("/diary")
async def read_diary():
    file_path = f"{DATA_PATH}/dagbok.csv"
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")

@app.post("/query")
async def search_vector_db(query: Prompt):
    result = await diary_agent.run(query.prompt)
    
    return result.output

@app.post("/add_text")
async def add_text(query: Prompt):
    result = await stt_agent.run(f"Analysera detta dagboksinlägg: {query.prompt}")
    
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weekday": datetime.now().strftime("%A").capitalize(),
        "activity": result.output.activity,
        "feelings": result.output.feelings,
        "mood": result.output.mood
    }
    print(new_entry)
    add_data(new_entry)
    
    return new_entry
    
@app.post("/science_query")
async def search_vector_db_science_table(query: Prompt):
    result = await science_agent.run(query.prompt)
    
    return result.output


model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="sv")
    # Slå ihop alla segment till en sträng
    text = " ".join([segment.text for segment in segments])
    
    return text.strip()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    audio_file = io.BytesIO(audio_bytes)
    
    transcribed_text = transcribe_audio(audio_file)
    
    result = await diary_agent.run(transcribed_text)
    
    communicate = edge_tts.Communicate(result.output.answer, "sv-SE-SofieNeural")
    audio_output = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_output.write(chunk["data"])
    
    audio_output.seek(0)
    
    return Response(content=audio_output.getvalue(), media_type="audio/wav")
    
    