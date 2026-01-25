import lancedb
import pandas as pd
from backend.data_models import Daily_mood, Article
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
import time

def setup_vector_db(path=VECTOR_DATABASE_PATH):
    vector_db = lancedb.connect(uri=path)
    
    vector_db.create_table(name="diary", schema=Daily_mood, mode="overwrite")
    vector_db.create_table(name="science", schema=Article, mode="overwrite")
    
    return vector_db

def ingest_csv_to_vector_db(table):
    file_path = DATA_PATH / "dagbok.csv"
    df = pd.read_csv(file_path)
    
    # Lägger in activity, mood och veckodag i content för vektorsökning
    df['content'] =  "Veckodag: " + df['weekday'] + ". Aktivitet: " + df['activity'] + ". Mående: " + df['mood']
    
    table.add(df.to_dict(orient="records"))
    
def ingest_txt_to_vector_db(table, file_path, chunk_size=1000):
    """Läser .txt, chunkar och laddar upp batch-vis för att undvika att slå i taket."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skapa chunks
    raw_chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    data_to_ingest = []
    for chunk in raw_chunks:
        if chunk.strip():
            data_to_ingest.append({
                "title": file_path.stem, 
                "content": chunk
            })
    
    # Ladda upp i batcher, gemini funkar inte med för många anrop, men klarar många embeddings per anrop.
    BATCH_SIZE = 50 
    
    for i in range(0, len(data_to_ingest), BATCH_SIZE):
        batch = data_to_ingest[i:i+BATCH_SIZE]
        
        try:
            table.add(batch)
            print(f"Sparade batch {i} till {i + len(batch)} av {len(data_to_ingest)}")
        except Exception as e:
            print(f"Fel vid batch {i}: {e}")
            time.sleep(5) # Vänta längre om det blir fel
            
        # Kort paus
        time.sleep(1)

if __name__ == "__main__":
    print("Sätter upp LanceDB...")
    db = setup_vector_db()
    
    diary_table = db.open_table("diary")
    science_table = db.open_table("science")
    
    ingest_csv_to_vector_db(diary_table)
    ingest_txt_to_vector_db(science_table, DATA_PATH / "whr25.txt", chunk_size=1000)
    
    print("Db klar!")