import lancedb
import pandas as pd
from backend.data_models import Daily_mood, Article, News
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
import time
import json

def setup_vector_db(path=VECTOR_DATABASE_PATH):
    vector_db = lancedb.connect(uri=path)
    
    # vector_db.create_table(name="diary", schema=Daily_mood, mode="overwrite")
    # vector_db.create_table(name="science", schema=Article, mode="overwrite")
    vector_db.create_table(name="news", schema=News, mode="overwrite")
    
    return vector_db

def ingest_csv_to_vector_db(table):
    file_path = DATA_PATH / "dagbok.csv"
    df = pd.read_csv(file_path)
    
    # Lägger in activity, mood och veckodag i content för vektorsökning
    # första bokstaven stor på mood och feelings
    df['content'] = (
        "Veckodag: " + df['weekday'] + 
        ". Aktivitet: " + df['activity'].str.capitalize() + 
        ". Mående: " + df['feelings'].str.capitalize() + 
        ". Humör: " + df['mood'].str.capitalize() +
        ". Nyckelord: " + df['keywords'].str.capitalize()

    )
    
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


def ingest_crawl_to_vector_db(table, file_path): 
    """
    Läser in json fil till vectorDB med batches
    """
    df_cleaned = pd.read_json(file_path)
    batch_size = 50

    df_cleaned["date"] = pd.to_datetime(df_cleaned["date"]).dt.strftime('%Y-%m-%d')
    print(f"data will be loaded in batches of batch size: {batch_size}")
    for i in range(0, len(df_cleaned), batch_size):
        print("starting to load crawl data")
        batch_df = df_cleaned.iloc[i:i + batch_size]

        #merge_insert så man inte lägger in dubletter
        table.merge_insert("title").when_matched_update_all().when_not_matched_insert_all().execute(batch_df)
        print(f"batch {i}/{len(df_cleaned) / batch_size} finished, sleeping for 30 seconds")
        time.sleep(30) 
        print("sleep finished")


if __name__ == "__main__":
    print("Sätter upp LanceDB...")
    db = setup_vector_db()
    
    # diary_table = db.open_table("diary")
    # science_table = db.open_table("science")
    news_table = db.open_table("news")
    
    # ingest_csv_to_vector_db(diary_table)
    # ingest_txt_to_vector_db(science_table, DATA_PATH / "whr25.txt", chunk_size=1000)
    # ingest_txt_to_vector_db(science_table, DATA_PATH / "the-perma-model.txt", chunk_size=1000)
    ingest_crawl_to_vector_db(news_table, DATA_PATH / "omni_cleaned.json")
    print("Db klar!")