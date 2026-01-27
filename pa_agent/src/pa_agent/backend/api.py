from fastapi import FastAPI, UploadFile, File
from rag_agent import diary_agent, science_agent
from stt_agents import stt_agent
from data_models import Prompt
from datetime import datetime
import locale
from data_ingestion import add_data
from constants import DATA_PATH
import pandas as pd
from voice_transcription import transcribe_audio, transcribe_text
import base64

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


@app.post("/text_input")
async def text_input(query: Prompt):
    text_input = query.prompt
    
    output_text = await route_input(text_input)

    audio_output = await transcribe_text(output_text)
    
    audio_base64 = base64.b64encode(audio_output).decode('utf-8')

    return {
        "text_input": text_input,
        "text_output": output_text,
        "audio": audio_base64
    }



@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcribed_text = await transcribe_audio(audio_bytes)
    
    output_text = await route_input(transcribed_text)
        
    audio_output = await transcribe_text(output_text)
    
    audio_base64 = base64.b64encode(audio_output).decode('utf-8')
    
    return {
        "text_input": transcribed_text,
        "text_output": output_text,
        "audio": audio_base64
    }

# Borde det vara en annan agent eller ska det va samma som bara får ny prompt?    
async def route_input(text: str) -> str:
    prompt = f"""
    Du är en router-agent. Din uppgift är att kategorisera användarens input.
    Input: "{text}"
    
    Välj en av följande kategorier:
    - ENTRY: Om användaren berättar om sin dag, sina känslor eller vad de har gjort (t.ex. "Idag känner jag mig glad och jag har tränat").
    - QUERY: Om användaren ställer en fråga om sitt förflutna eller sin dagbok (t.ex. "Hur mådde jag förra veckan?").
    
    Svara endast med ordet ENTRY eller QUERY.
    """
    
    intent = await diary_agent.run(prompt) 
    
    if intent.output.answer.strip() == "ENTRY":
        result = await stt_agent.run(f"Analysera detta dagboksinlägg: {text}")
    
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": datetime.now().strftime("%A").capitalize(),
            "activity": result.output.activity,
            "feelings": result.output.feelings,
            "mood": result.output.mood
        }
        add_data(new_entry)
        
        output_text = f"Jag har sparat ditt inlägg i dagboken. {new_entry}"
        
    else:
        text = f"Dagens datum: {datetime.now().strftime("%Y-%m-%d")} - {text}"
        result = await diary_agent.run(text)
        
        output_text = result.output.answer
    
    return output_text