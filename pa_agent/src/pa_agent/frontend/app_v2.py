import os
import streamlit as st
import requests
from css import get_css
import base64
from plots import line_plot, pie_plot, plot_keyword_sunburst, plot_negative_triggers, plot_combined_triggers
from utils import load_data, show_activities, give_helpful_advices, show_kpis, show_trend

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

get_css()
     
def layout():

    load_data()
    df = st.session_state["df"]
    
    # Side bar meny
    with st.sidebar:
        st.title("dAgent")
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
                
                st.divider()
                
                st.subheader("This made you feel shitty..")
                
                mood = "negativt"
                activities = show_activities(df, mood)
                formatted_text = "\n".join([f"{i+1}. {activity}\n" for i, activity in enumerate(activities)])
                
                st.write(formatted_text)
                                
                st.divider()
                
                # --- KPIS ---
                percentage, worst_day, streak = show_kpis(df, mood)
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                with col_kpi1:
                    st.metric("Percentage", percentage)
                with col_kpi2:
                    st.metric("Worst Day", worst_day)
                with col_kpi3:
                    st.metric("Longest Streak", f"{streak} days")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                guidance_button = st.button("Hit for guidance?")           
                if guidance_button:
                    st.markdown(give_helpful_advices(df, mood))

        with col2:
            # centrerad rubrik - måste va här tydligen.......
            st.markdown("""
                <h2 style='text-align: center; margin-bottom: 0; color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>
                    the dAgent
                </h2>
                <hr style='margin: 10px 0 30px 0; opacity: 0.3;'>
            """, unsafe_allow_html=True)

            audio = st.audio_input("Voice Input", label_visibility="collapsed")
            prompt = st.text_input("Whats on your mind?", placeholder="Just tell me dude..")

            st.divider()

            # audio
            if audio:
                files = {"file": ("recording.wav", audio, "audio/wav")}
                with st.spinner("Transcribing..."):
                    try:
                        response = requests.post(f"{BACKEND_BASE_URL}/transcribe", files=files)
                        if response.status_code == 200:
                            data = response.json()
                            
                            # visa användarens input
                            with st.chat_message("user"):
                                st.write(data["text_input"])
                            
                            # visa llm svar
                            with st.chat_message("assistant"):
                                st.write(data["text_output"])
                                # spela upp ljud
                                audio_bytes = base64.b64decode(data["audio"])
                                st.audio(audio_bytes, format="audio/wav", autoplay=True)
                        else:
                            st.error(f"Backend sucks: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

            # text
            if prompt:
                with st.spinner("Hmm..."):
                    try:
                        response = requests.post(f"{BACKEND_BASE_URL}/text_input", json={"prompt": prompt})
                        if response.status_code == 200:
                            data = response.json()
                            
                            # visa user input
                            with st.chat_message("user"):
                                st.write(prompt)
                            
                            # llm svar
                            with st.chat_message("assistant"):
                                st.write(data["text_output"])
                                
                                audio_bytes = base64.b64decode(data["audio"])
                                st.audio(audio_bytes, format="audio/wav", autoplay=True)
                        else:
                            st.error(f"Backend sucks: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

        with col3:
            with st.container():
                st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
                
                st.header("HAPPY PLACE")
                
                st.divider()
                
                st.subheader("Stick to the good stuff!")
                mood = "positivt"
                activities = show_activities(df, mood)
                formatted_text = "\n".join([f"{i+1}. {activity}\n" for i, activity in enumerate(activities)])
                st.write(formatted_text)
                
                st.divider()
                
                # --- KPIS ---
                percentage, best_day, streak = show_kpis(df, mood)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Percentage", percentage)
                with c2:
                    st.metric("Best Day", best_day)
                with c3:
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
        line_plot_mood = line_plot(diary_df, 'date', 'mood', ['activity', 'feelings'])
        st.plotly_chart(line_plot_mood, use_container_width=True)        
        
        
        # Plottar om keywords
        k_col1, k_col2 = st.columns(2)
        
        with k_col1:
            st.subheader("Top Bad Triggers")
            negative_triggers = plot_negative_triggers(diary_df)
            st.plotly_chart(negative_triggers, use_container_width=True)
            
        with k_col2:
            st.subheader("Pos. vs Neg. Keywords")
            keywords_sunburst = plot_keyword_sunburst(diary_df)
            st.plotly_chart(keywords_sunburst, use_container_width=True)

        keyword_plot=plot_combined_triggers(diary_df)
        st.plotly_chart(keyword_plot, use_container_width=True)
        
    elif page == "News":
        pass


if __name__ == "__main__":
    layout()