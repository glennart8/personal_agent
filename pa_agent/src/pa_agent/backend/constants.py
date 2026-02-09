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

# Sätt basmappen för projektet (repo-roten)
# Pathlib grundkurs:
# sparas importen som OBJEKT
# kan peka på både en folder och en fil - pathlib fattar vilket
# MAPPEN NUVARANDE FIL FINNS I = Path(__file__).resolve()
# Kör man på det systemet så spelar det ingen roll var i filsystem du står när du kör scriptet
# pathlib sköter inte IMPORTER utan pekar bara i filsystemt, importers sköts av sys.path, moduler o paket
# Varför det inte är en improt i python-mening är att du inte importerar någon kod som körs, en import = kör kod och stoppa i variabel

BASE_DIR = Path(__file__).resolve().parents[1]
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"