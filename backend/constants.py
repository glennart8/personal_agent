import os
from pathlib import Path

DATA_PATH = Path(__file__).parents[1] / "data"


DEFAULT_VECTOR_DATABASE_PATH = Path(__file__).parents[1] / "knowledge_base"
VECTOR_DATABASE_PATH = os.getenv("VECTOR_DATABASE_PATH", DEFAULT_VECTOR_DATABASE_PATH)