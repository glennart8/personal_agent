import os
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).parents[1] / "data"
DATA_PATH = os.getenv("DATA_PATH", DEFAULT_DATA_PATH)



DEFAULT_VECTOR_DATABASE_PATH = Path(__file__).parents[1] / "knowledge_base"
VECTOR_DATABASE_PATH = os.getenv("VECTOR_DATABASE_PATH", DEFAULT_VECTOR_DATABASE_PATH)


WEEKDAYS_SV = {
    "Monday": "Måndag",
    "Tuesday": "Tisdag",
    "Wednesday": "Onsdag",
    "Thursday": "Torsdag",
    "Friday": "Fredag",
    "Saturday": "Lördag",
    "Sunday": "Söndag"
}

