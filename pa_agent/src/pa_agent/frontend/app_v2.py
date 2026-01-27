import os
import streamlit as st
import requests
import pandas as pd
from css import get_css

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

get_css()

def load_data():
    # Hämta bara om data frame inte finns i minnet
    if "df" not in st.session_state:
        response = requests.get(f"{BACKEND_BASE_URL}/diary")
        st.session_state["df"] = pd.DataFrame(response.json())

def show_activities(df, mood: str, count = 5):
    """
    Use either 'positivt' or 'negativt' as in parameter
    Returns a list of activities which could be linked to negative feelings 
    """
    # Sortera ut alla poster med samma mood (pos/neg)
    df = df[df['mood'] == mood]
    
    # Få de mest förekommande aktiviteterna
    activities = df['activity'].value_counts().head(count).index.tolist()   
    
    return activities
    
# SKAPA EN METOD SOM TAR IN AKTIVITETERNA FRÅN SHOW_ACTIVITIES OCH HÄMTA HJÄLPSAM TEXT FRÅN SCIENCE     
    
def give_helpful_advices(df, mood: str):
    activities = show_activities(df, mood)
    
    if not activities:
        return "Inga aktiviteter att analysera."
    
    # Be LLM läsa listan och knyta an till forskning
    prompt = f"""Read the list of activities {activities} and find relevent science articles, 
                use them as guidance and advice the user to take them into consideration.
                Keep it short and to the point.
                Always respond in swedish!
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


def show_kpis(df, mood):
    # Procentsats över positivt/negativt
    total = len(df)
    df_mood = df[df['mood'] == mood] 
    percentage = f"{round(len(df_mood) / total * 100)}%"
    
    # Sämsta/bästa veckodagen
    worst_or_best_day = df[df['mood'] == mood]['weekday'].value_counts().idxmax()
    
    # Längsta streak
    streak = calculate_streak(df, mood)
    
    return percentage, worst_or_best_day, streak

def show_trend(df, num_days=3):
    # Visa grönt/rött beroende på om de senaste 3 dagarna är mest pos eller neg
    last_num_days = df.tail(num_days)['mood'].value_counts()
    pos_count = last_num_days.get('positivt', 0) # Krashar annars om pos / neg inte finns
    neg_count = last_num_days.get('negativt', 0)
    
    if pos_count > neg_count:
        st.success("Positiv trend", icon=":material/thumb_up:")
    else:
        st.error("Negativ trend", icon=":material/thumb_down:")     
     
def layout():

    load_data()
    df = st.session_state["df"]
    
    # Sidebar istället
    with st.sidebar:
        st.title("Personal Agent")
        page = st.radio(
            "Välj sida:",
            ["Dashboard", "Diary", "News"],
            label_visibility="collapsed"
        )
        
        show_trend(df)
      
    if page == "Dashboard":
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                
                st.header("DARK SIDE")
                st.subheader("This made you feel shitty..")
                
                mood = "negativt"
                activities = show_activities(df, mood)
                formatted_text = "\n".join([f"{i+1}. {activity}\n" for i, activity in enumerate(activities)])
                
                st.write(formatted_text)
                
                # --- KPIS ---
                percentage, worst_day, streak = show_kpis(df, mood)
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                with col_kpi1:
                    st.metric("Percentage", percentage)
                with col_kpi2:
                    st.metric("Worst Day", worst_day)
                with col_kpi3:
                    st.metric("Longest Streak", f"{streak} days")
                                       
                #st.write(give_helpful_advices(df, mood))
                st.markdown(give_helpful_advices(df, mood))
                
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.header("Whats on your mind?")
            user_input = st.text_input(label="Please, just tell me..")
            
            if user_input:
                pass
                
            # AUDIO INPUT    
            audio = st.audio_input("Record")
            if audio:
                # text = transcribe_audio(audio)
                files = {"file": ("recording.wav", audio, "audio/wav")}
                # st.write(text)
                response = requests.post(f"{BACKEND_BASE_URL}/transcribe", files=files)
                
                if response.status_code == 200:
                    audio_output = response.content
                    
                    st.audio(audio_output, format="audio/wav", autoplay=True)
                
                else:
                    st.error("Backend suger")

        with col3:
            with st.container(border=True):
                st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
                
                st.header("HAPPY PLACE")
                st.subheader("Stick to the good stuff!")
                mood = "positivt"
                activities = show_activities(df, mood)
                formatted_text = "\n".join([f"{i+1}. {activity}\n" for i, activity in enumerate(activities)])
                st.write(formatted_text)
                
                percentage, best_day, streak = show_kpis(df, mood)
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                with col_kpi1:
                    st.metric("Percentage", percentage)
                with col_kpi2:
                    st.metric("Best Day", best_day)
                with col_kpi3:
                    st.metric("Longest Streak", f"{streak} days")
                
                st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Diary":
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Diary")
            diary_df = df.sort_values(by="date", ascending=False)
            st.dataframe(diary_df, use_container_width=True)
        
        with col2:
            pass

    elif page == "News":
        pass

if __name__ == "__main__":
    layout()