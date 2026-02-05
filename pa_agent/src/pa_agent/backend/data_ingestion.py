import lancedb
from constants import VECTOR_DATABASE_PATH, DATA_PATH
import pandas as pd
import time

def add_data(data: dict, table: str = "diary"):
    db = lancedb.connect(VECTOR_DATABASE_PATH)
    
    file_path = f"{DATA_PATH}/dagbok.csv"
    
    print("Sparar data...")
    
    df = pd.read_csv(file_path)
    new_df = pd.DataFrame([data])
    df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    print(df)
    
    new_df['content'] = (
        "Veckodag: " + new_df['weekday'] + 
        ". Aktivitet: " + new_df['activity'].str.capitalize() + 
        ". Mående: " + new_df['feelings'].str.capitalize() + 
        ". Humör: " + new_df['mood'].str.capitalize() 
    )
    
    db[table].add(new_df)
    
    print("Data sparad")
    
    
async def ingest_crawl_to_vector_db(file_path: str): 
    """
    Läser in json fil till vectorDB med batches
    """
    db = lancedb.connect(VECTOR_DATABASE_PATH)
    table = db["news"]
    
    df_cleaned = pd.read_json(file_path)
    batch_size = 50
    sleep_time = 30

    df_cleaned["date"] = pd.to_datetime(df_cleaned["date"]).dt.strftime('%Y-%m-%d')
    df_cleaned["mood"] = df_cleaned["mood"].str.capitalize()
    
    print(f"\n\nData will be loaded in batches of batch size: {batch_size}\n\n")
    for i in range(0, len(df_cleaned), batch_size):
        print("\nStarting to load data...\n")
        batch_df = df_cleaned.iloc[i:i + batch_size]

        #merge_insert så man inte lägger in dubletter
        table.merge_insert("title").when_matched_update_all().when_not_matched_insert_all().execute(batch_df)
        print(f"Finished loading batch {i}-{i+batch_size if i+batch_size < len(df_cleaned) else len(df_cleaned)} of {len(df_cleaned)}\nSleeping for {sleep_time} seconds")
        time.sleep(sleep_time) 
        
    print("Load finished")