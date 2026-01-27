import os
import streamlit as st
import requests
from css import get_css
import base64
from plots import line_plot, pie_plot
from utils import load_data, show_activities, give_helpful_advices, show_kpis, show_trend

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

get_css()
     
def layout():

    load_data()
    df = st.session_state["df"]
    
    # Side bar meny
    with st.sidebar:
        st.title("dAygent")
        page = st.radio(
            "Välj sida:",
            ["Dashboard", "Diary", "News"],
            label_visibility="collapsed"
        )
        
        show_trend(df)
      
    if page == "Dashboard":
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container():
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
                           
                #st.markdown(give_helpful_advices(df, mood))
                
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.header("Whats on your mind?")
            
            audio = st.audio_input("Please, say something..")
            chat_input = st.chat_input("Just tell me..")
            
            if audio:
                files = {"file": ("recording.wav", audio, "audio/wav")}
                with st.spinner("Transkriberar..."):
                    response = requests.post(f"{BACKEND_BASE_URL}/transcribe", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.write(data["text_input"])
                        
                        # Gör om base64-strängen tillbaka till bytes för uppspelning
                        audio_bytes = base64.b64decode(data["audio"])
                        st.audio(audio_bytes, format="audio/wav", autoplay=True)

                        st.write(data["text_output"])  # Visa texten
                        
                    else:
                        st.error("Backend suger")
                        
            if chat_input:
                with st.spinner("Tänker..."):
                    response = requests.post(f"{BACKEND_BASE_URL}/text_input", json={"prompt": chat_input})
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.write(data["text_input"])
                        
                        # Gör om base64-strängen tillbaka till bytes för uppspelning
                        audio_bytes = base64.b64decode(data["audio"])
                        st.audio(audio_bytes, format="audio/wav", autoplay=True)

                        st.write(data["text_output"])  # Visa texten
                        
                    else:
                        st.error("Backend suger")

        with col3:
            with st.container():
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
            # Pie plot som visar mood över veckodagarna
            pie_plot_mood_weekdays = pie_plot(diary_df, diary_df['weekday'], diary_df['mood'])
            st.plotly_chart(pie_plot_mood_weekdays, use_container_width=True)
              
        # Line plot som visar mood över tid
        line_plot_mood = line_plot(diary_df, diary_df['date'], diary_df['mood'], ['activity', 'feelings'])
        st.plotly_chart(line_plot_mood, use_container_width=True)        
            

    elif page == "News":
        pass




if __name__ == "__main__":
    layout()