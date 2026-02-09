import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_URL")


WEEKDAYS_SV = {
    "Monday": "Måndag",
    "Tuesday": "Tisdag",
    "Wednesday": "Onsdag",
    "Thursday": "Torsdag",
    "Friday": "Fredag",
    "Saturday": "Lördag",
    "Sunday": "Söndag"
}

# För pills i chat-botten
SUGGESTIONS_NEWS = {
    "⚽ Sport": "Ge mig de senaste sport-nyheterna",
    "🚗 Bilar": "Nyheter inom bilindustrin",
    "💰 Krypto": "Senaste inom krypto",
    "🤖 AI": "Senaste inom AI"
}

SUGGESTIONS_DIARY = {
    "🌿 Vad ger mig ro?": "Vad har jag skrivit att jag blir lugn och avslappnad av?",
    "📉 När blir jag nedstämd?": "Analysera när och varför jag känner mig nedstämd.",
    "😄 Vad gör mig glad?": "Vilka aktiviteter verkar göra mig på bäst humör?",
    "📅 Sammanfatta veckan": "Ge mig en kort sammanfattning av hur jag mått den senaste veckan."
}

def load_data():
    # Hämta bara om data frame inte finns i minnet
    if "diary" not in st.session_state:
        update_diary()

    if "news" not in st.session_state:
        update_news()

    if "df" not in st.session_state:
        st.session_state["df"] = st.session_state["diary"]


def update_diary():
    response = requests.get(f"{BACKEND_BASE_URL}/diary")
    df = st.session_state['diary'] = pd.DataFrame(response.json())
    
    return df

def update_news():
    response = requests.get(f"{BACKEND_BASE_URL}/news")
    df = st.session_state["news"] = pd.DataFrame(response.json())
    
    return df


def init_state():
    st.session_state.setdefault("messages_diary", [])
    st.session_state.setdefault("messages_news", [])
    st.session_state.setdefault("neg_guidance_text", None)
    st.session_state.setdefault("pos_guidance_text", None)


def show_activities(df, mood: str, column=None, count = 5):
    """
    Use either 'positivt' or 'negativt' as in parameter
    Returns a list of activities which could be linked to negative feelings 
    """
    # Sortera ut alla poster med samma mood (pos/neg)
    df = df[df['mood'] == mood]
    
    # Få de mest förekommande aktiviteterna
    activities = df[column].value_counts().head(count).index.tolist()   
    activities = [a.strip() for a in activities]
    
    return activities
    
# SKAPA EN METOD SOM TAR IN AKTIVITETERNA FRÅN SHOW_ACTIVITIES OCH HÄMTA HJÄLPSAM TEXT FRÅN SCIENCE     
# Borde man kasta in en knapp som aktiverar denna?
    
def give_helpful_advices(df, mood: str, column = None):
    activities = show_activities(df, mood, column)
    
    if not activities:
        return "Inga aktiviteter att analysera."
    

    #     # Be LLM läsa listan och knyta an till forskning
    prompt = f""" 
        Read the list of activities {activities} and find relevent science articles, 
        use them as guidance, advice and motivation for the user.
        Keep it short and to the point.
    """ 
        
    try:                
        response = requests.post(f"{BACKEND_BASE_URL}/science_query", json={"prompt": prompt})
        data = response.json()
        return data.get("answer", "Kunde inte tolka svaret.")
    
    except Exception as e:
        return f"Anslutningsfel: {e}"
    
    
def calculate_streak(df, mood):
    # Skapa en boolean serie för mood, om det matchar blir det true
    is_mood = df['mood'] == mood
    
    max_streak = 0
    current_streak = 0
    
    for value in is_mood:
        if value: # om det matchar (true) med mood som skickats in 
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def show_kpis(df, mood, column):
    # Procentsats över positivt/negativt
    total = len(df)
    df_mood = df[df['mood'] == mood] 
    percentage = f"{round(len(df_mood) / total * 100)}%"
    
    # Sämsta/bästa veckodagen
    worst_or_best_day = df[df['mood'] == mood][column].value_counts().idxmax()
    
    # Längsta streak
    streak = calculate_streak(df, mood)
    
    return percentage, worst_or_best_day, streak

def show_trend(df, num_days=3):
    
    if df is None:
        return
    
    # Visa grönt/rött beroende på om de senaste 3 dagarna är mest pos eller neg
    last_num_days = df.tail(num_days)['mood'].value_counts()
    pos_count = last_num_days.get('Positivt', 0) # Krashar annars om pos / neg inte finns
    neg_count = last_num_days.get('Negativt', 0)
    
    if pos_count > neg_count:
        st.success("Positive trend", icon=":material/thumb_up:")
    else:
        st.error("Negative trend", icon=":material/thumb_down:")     
     
     
def get_exploded_keywords(df):
    all_keywords = df.copy()
    
    # dela upp strängen "Jobb, Stress" till en lista ["Jobb", "Stress"]
    all_keywords['keyword'] = all_keywords['keywords'].astype(str).str.split(',')
    
    # explodera listan (skapar en ny rad för varje keyword)
    all_keywords = all_keywords.explode('keyword')
    
    # ta bort whitespace
    all_keywords['keyword'] = all_keywords['keyword'].str.strip()
    
    return all_keywords
