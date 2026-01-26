from fastapi import FastAPI
from rag_agent import diary_agent, science_agent
from stt_agents import stt_agent
from data_models import Prompt
from datetime import datetime
import locale
from data_ingestion import add_data

# Måste ha detta för att få ut svenska ord för veckodagarna..........
try:
    locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")
except:
    pass # Blir engelska ord i stället

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Health check"}

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