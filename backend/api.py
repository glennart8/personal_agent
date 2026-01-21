from fastapi import FastAPI
from rag_agent import diary_agent
from data_models import Prompt


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Health check"}

@app.post("/query")
async def search_vector_db(query: Prompt):
    result = await diary_agent.run(query.prompt)
    
    return result.output