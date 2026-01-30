from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Literal

load_dotenv()

embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")

# För sökning i V-db
class Daily_mood(LanceModel):
    activity: str
    feelings: str
    mood: str
    keywords: str
    date: datetime = Field(default_factory=datetime.now)
    weekday: str
    content: str = embedding_model.SourceField()
    embedding: Vector(dim=3072) = embedding_model.VectorField()

# För STT    
class DiaryExtraction(BaseModel):
    activity: str = Field(description="A short summary of what the user did the current day")
    feelings: str = Field(description="A word or short frase, describing the mood of the user")
    mood: str = Field(description="Positive or negative")
    keywords: str = Field(description="Extract 1-3 tags/keywords that categorize the entry, e.g. ['Jobb', 'Sömn', 'Kodning', 'Relationer', 'Träning']")

# För sökning av nyhetsartiklar i V-db
class News(LanceModel):
    news_section: str
    title: str = embedding_model.SourceField()
    date : datetime.date
    teaser_text: str = embedding_model.SourceField()
    image_url: str
    image_description: str
    embedding: Vector(dim=3072) = embedding_model.VectorField()

class RagResponse(BaseModel):
    answer: str = Field(description="answer based on the retrieved file")
    
class Prompt(BaseModel):
    prompt: str = Field(description="prompt from user, if empty consider it as missing")

# För vetenskapliga artiklar
class Article(LanceModel):
    title: str
    content: str = embedding_model.SourceField()
    embedding: Vector(dim=3072) = embedding_model.VectorField()
    
class RoutingDescision(BaseModel):
    intent: str = Literal["ENTRY", "QUERY"]

# En klass så vi kan använda olika röster
# Använder Path för att kunna köra stem() och read_text()
class TTSConfig(BaseModel):
    input_file: Path = Field(..., description="Sökväg till textfilen som ska läsas")
    output_file: Optional[Path] = None
    voice: str = Field("sv-SE-SofieNeural") # "sv-SE-MattiasNeural"

