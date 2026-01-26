import lancedb
from constants import VECTOR_DATABASE_PATH, DATA_PATH
import pandas as pd

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
        "Veckodag: " + df['weekday'] + 
        ". Aktivitet: " + df['activity'].str.capitalize() + 
        ". Mående: " + df['feelings'].str.capitalize() + 
        ". Humör: " + df['mood']
    )
    
    db[table].add(new_df)
    
    print("Data sparad")
    
    
    