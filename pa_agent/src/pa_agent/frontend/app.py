import os
import streamlit as st
import requests
import pandas as pd
from css import get_css

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

get_css()

def show_activities(mood: str, count = 5):
    """
    Use either 'positivt' or 'negativt' as in parameter
    Returns a list of activities which could be linked to negative feelings 
    """
    response = requests.get(f"{BACKEND_BASE_URL}/diary")
    df = pd.DataFrame(response.json())
    df = df[df['mood'] == mood]
    
    # Få de mest förekommande aktiviteterna
    activities = df['activity'].value_counts().head(count).index.tolist()
    
    # Formatera som text
    return "\n".join([f"{activity}\n" for activity in activities])
    
    
def layout():
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Diary", "News"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                
                st.header("DARK SIDE")
                st.subheader("This makes you feel shitty..")
                mood = "negativt"
                activities = show_activities(mood)
                st.write(activities)
                
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
            activities = show_activities(mood)
            st.write(activities)
            
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Diary")
            response = requests.get(f"{BACKEND_BASE_URL}/diary")
            df = pd.DataFrame(response.json())
            df = df.sort_values(by="date", ascending=False)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            pass


    with tab3:
        pass

if __name__ == "__main__":
    layout()