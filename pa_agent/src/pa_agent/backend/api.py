from fastapi import FastAPI, UploadFile, File
from rag_agent import diary_agent, science_agent, stt_agent, route_agent, news_agent 
from data_models import Prompt
from datetime import datetime
import locale
from data_ingestion import add_data
from constants import DATA_PATH
import pandas as pd
from voice_transcription import transcribe_audio, transcribe_text
import base64
import time
from pydantic_ai import UsageLimits, UsageLimitExceeded

try:
    locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")
except:
    pass 

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Health check"}


#region DIARY
@app.get("/diary")
async def read_diary():
    file_path = f"{DATA_PATH}/dagbok.csv"
    df = pd.read_csv(file_path)
    
    return df.to_dict(orient="records") 
    
    
@app.post("/science_query")
async def search_vector_db_science_table(query: Prompt):
    result = await science_agent.run(query.prompt)
    
    return result.output


@app.post("/text_input/diary")
async def text_input(query: Prompt) -> dict:
    text_input = query.prompt
    
    output_text = await route_input(text_input)

    audio_output = await transcribe_text(output_text)
    
    audio_base64 = base64.b64encode(audio_output).decode('utf-8')

    return {
        "text_input": text_input,
        "text_output": output_text,
        "audio": audio_base64
    }
    

@app.post("/transcribe/diary")
async def transcribe(file: UploadFile = File(...)) -> dict:
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
    
    
#region NEWS   
@app.get("/news")
async def read_news():
    file_path = f"{DATA_PATH}/omni_cleaned_with_keywords.json"
    df = pd.read_json(file_path).sort_values(by="date", ascending=True).reset_index()
    
    return df.to_dict(orient="records")       
    
    
@app.post("/text_input/news")
async def text_input(query: Prompt) -> dict:
    
    # Sätter gräns för att undvika oändliga loopar som kostar fan
    limits = UsageLimits(request_limit=5)
    
    try:
        result = await news_agent.run(query.prompt, usage_limits=limits)
        news_obj = result.output
        
        # bygger texten manuellt med BARA title och teaser_text
        script = ""
        
        for article in news_obj.articles:
            script += f"{article.title}. {article.teaser_text}. "
        
        # tar bort markdown-shit
        answer_text = script.replace("*", "").replace("#", "")

        audio_output = await transcribe_text(answer_text)
        audio_base64 = base64.b64encode(audio_output).decode('utf-8')

        return {
            "text_input": query.prompt,
            "text_output": answer_text,
            "audio": audio_base64
        }
        
    except UsageLimitExceeded:
        fallback_text = "Jag fastnade i en sök-loop och avbröt för att spara pengar. Försök vara mer specifik."
        
        return {
            "text_input": query.prompt,
            "text_output": fallback_text,
            "audio": None 
        }
            
    
# @app.post("/transcribe/news")
# async def transcribe(file: UploadFile = File(...)) -> dict:
#     audio_bytes = await file.read()
#     transcribed_text = await transcribe_audio(audio_bytes)
    
#     # Skicka text till agent
    
    
    
            
#     audio_output = await transcribe_text(output_text)
    
#     audio_base64 = base64.b64encode(audio_output).decode('utf-8')
    
#     return {
#         "text_input": transcribed_text,
#         "text_output": output_text,
#         "audio": audio_base64
#     }

# region ROUTE
async def route_input(text: str) -> str:
    intent = await route_agent.run(text) 

    time.sleep(2)

    if intent.output.intent.strip() == "ENTRY":
        result = await stt_agent.run(f"Analysera detta dagboksinlägg: {text}")

        time.sleep(2)

        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": datetime.now().strftime("%A").capitalize(),
            "activity": result.output.activity.capitalize(),
            "feelings": result.output.feelings.capitalize(),
            "mood": result.output.mood.capitalize(),
            "keywords": result.output.keywords.capitalize()
        }
        add_data(new_entry)

        output_text = f"Sparat ditt inlägg i dagboken. {new_entry['activity']}."

    else:
        text = f"Dagens datum: {datetime.now().strftime("%Y-%m-%d")} - {text}"
        result = await diary_agent.run(text)

        output_text = result.output.answer

    return output_text