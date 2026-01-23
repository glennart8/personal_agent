import lancedb
import pandas as pd
from backend.data_models import Daily_mood
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH

def setup_vector_db(path=VECTOR_DATABASE_PATH):
    vector_db = lancedb.connect(uri = path)
    vector_db.create_table(name = "diary", schema=Daily_mood, mode="overwrite")
    
    return vector_db


def ingest_docs_to_vector_db(table):
    file_path = DATA_PATH / "dagbok.csv"
    df = pd.read_csv(file_path)
    
    # Lägger in activity, mood och veckodagi content för vektorsökning
    df['content'] =  "Veckodag: " + df['weekday'] + ". Aktivitet: " + df['activity'] + ". Mående: " + df['mood']
    
    table.add(df.to_dict(orient="records"))
    

if __name__ == "__main__":
    print("Sätter upp LanceDB...")
    db = setup_vector_db()
    table = db.open_table("diary")
    
    ingest_docs_to_vector_db(table)
    
    print(table.to_pandas().head())
    
    print("Db klar!")