from pydantic import BaseModel, Field
from datetime import datetime
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv

load_dotenv()

embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")

class Daily_mood(LanceModel):
    activity: str
    mood: str
    date: datetime = Field(default_factory=datetime.now)
    weekday: str
    content: str = embedding_model.SourceField()
    embedding: Vector(dim=3072) = embedding_model.VectorField()
    
    
class RagResponse(BaseModel):
    answer: str = Field(description="answer based on the retrieved file")
    
class Prompt(BaseModel):
    prompt: str = Field(description="prompt from user, if empty consider it as missing")
    