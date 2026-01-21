from fastapi import FastAPI
from rag_agent import rag_agent
from data_models import Prompt


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Health check"}

@app.post("/query")
async def search_vector_db(query: Prompt):
    result = await rag_agent.run(query.prompt)
    
    return result.output