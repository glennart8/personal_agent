import os
import streamlit as st
import requests
import pandas as pd
from css import get_css

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

get_css()


def show_activities(df, mood: str, count = 5):
    """
    Use either 'positivt' or 'negativt' as in parameter
    Returns a list of activities which could be linked to negative feelings 
    """
    df = df[df['mood'] == mood]
    
    # Få de mest förekommande aktiviteterna
    activities = df['activity'].value_counts().head(count).index.tolist()
    
    # Formatera som text
    return "\n".join([f"{i+1}. {activity}\n" for i, activity in enumerate(activities)])
    
    
def show_kpis(df, mood):
    all = len(df)
    df_mood = df[df['mood'] == mood] 
    percentage = f"{round(len(df_mood) / all * 100)}%"
    
    # MIN SÄMSTA DAG
    worst_or_best_day = df[df['mood'] == mood]['weekday'].value_counts().idxmax()
    
    return percentage, worst_or_best_day
    
     
def layout():
    response = requests.get(f"{BACKEND_BASE_URL}/diary")
    df = pd.DataFrame(response.json())
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Diary", "News"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                
                st.header("DARK SIDE")
                st.subheader("This makes you feel shitty..")
                mood = "negativt"
                activities = show_activities(df, mood)
                st.write(activities)
                
                # --- KPIS ---
                st.write(show_kpis(df, mood))
                                
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.header("WZUP?!")
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
            st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
            
            st.header("HAPPY PLACE")
            st.subheader("Sunshine, melted ice cream and drink sticks")
            mood = "positivt"
            activities = show_activities(df, mood)
            st.write(activities)
            
            st.write(show_kpis(df, mood))
            
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Diary")
            diary_df = df.sort_values(by="date", ascending=False)
            st.dataframe(diary_df, use_container_width=True)
        
        with col2:
            pass

    with tab3:
        pass

if __name__ == "__main__":
    layout()