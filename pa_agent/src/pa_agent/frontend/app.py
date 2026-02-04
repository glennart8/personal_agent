import pandas as pd
import streamlit as st
import requests
from css import get_css
import base64
from plots import pie_plot, plot_keyword_sunburst, plot_negative_triggers, plot_combined_triggers, timeline_plot, scatter_plot
from utils import load_data, show_activities, give_helpful_advices, show_kpis, show_trend, init_state, update_diary, SUGGESTIONS_NEWS, SUGGESTIONS_DIARY, BACKEND_BASE_URL


get_css()

def sidebar_layout():
    with st.sidebar:
        # DIARY / NEWS
        app_mode = st.radio(
            "Välj läge:",
            ["Diary", "News"],
            horizontal=True, 
            label_visibility="collapsed"
        )

        st.divider()
        st.title("dAgent")

        load_data()
        df = st.session_state["df"]

        if app_mode == "Diary":
            menu = ["Dashboard", "Stats", "Read Diary"]
        else:
            menu = ["Dashboard", "Stats", "Read News"]

        page = st.radio(
            "Välj sida:",
            menu,
            label_visibility="collapsed"
        )
        
        show_trend(df)
        
        return app_mode, page
     

def col_2(app_mode):
    if app_mode == "Diary":
        suggestions = SUGGESTIONS_DIARY
        # Skriv ut gammal historik FÖRST 
        for message in st.session_state.messages_diary:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    if app_mode == "News":
        suggestions = SUGGESTIONS_NEWS
        # Skriv ut gammal historik FÖRST 
        for message in st.session_state.messages_news:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    # Centrerad rubrik och mer marginal, padding elelr va fan det hter mellan ljud o knapp
    st.markdown("""
        <h2 style='text-align: center; margin-bottom: 0; color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>
            the dAgent
        </h2>
        <hr style='margin: 10px 0 30px 0; opacity: 0.3;'> 
    """, unsafe_allow_html=True) 


    chat_input_choice = st.chat_input("Just tell me dude..")
                                    
    # Visa "Pills" (Knapparna)
    selected_pill = st.pills(
        "Förslag",
        options=suggestions.keys(), # sport, bilar osv
        label_visibility="collapsed",
        selection_mode="single",
        key=f"{app_mode}_pills"
    )
    
    # Om man skrivit i rutan gäller det, annars kollar vi om man klickat på en pill
    prompt = None
    
    if chat_input_choice:
        prompt = chat_input_choice
    elif selected_pill:
        # hämta value - den långa frågan baserat på key
        prompt = suggestions[selected_pill]

    button_col, mic_col = st.columns([0.2, 0.8], gap="small", vertical_alignment="center")

    with button_col:
        send_clicked = st.button("Send", type="primary", use_container_width=True)

    with mic_col:
        audio = st.audio_input("Voice", label_visibility="collapsed")

    st.divider()


    if audio and send_clicked:
        files = {"file": ("recording.wav", audio, "audio/wav")}
        with st.spinner("Transcribing..."):
            try:
                response = requests.post(f"{BACKEND_BASE_URL}/transcribe/{app_mode.lower()}", files=files)
                if response.status_code == 200:
                    data = response.json()
                    
                    with st.chat_message("user"):
                        st.write(data["text_input"])
                    
                    with st.chat_message("assistant"):
                        st.write(data["text_output"])
                        if data.get("audio"):
                            audio_bytes = base64.b64decode(data["audio"])
                            st.audio(audio_bytes, format="audio/wav", autoplay=True)
                    
                    if "df" in st.session_state:
                        del st.session_state["df"]

                else:
                    st.error(f"Backend sucks: {response.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
                    

    # TEXT
    elif prompt:
        st.session_state.messages_news.append({"role": "user", "content": prompt})
                        
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{BACKEND_BASE_URL}/text_input/{app_mode.lower()}", json={"prompt": prompt})
                if response.status_code == 200:
                    data = response.json()
                    
                    answer_text = data["text_output"]
                    
                    st.session_state.messages_news.append({"role": "assistant", "content": answer_text})
                    
                    with st.chat_message("assistant"):
                        st.write(data["text_output"])
                        if data.get("audio"):
                            audio_bytes = base64.b64decode(data["audio"])
                            st.audio(audio_bytes, format="audio/wav", autoplay=True)
                                
                    if "df" in st.session_state:
                        del st.session_state["df"]

                else:
                    st.error(f"Backend sucks: {response.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
   
     
def layout():
    init_state() # Ladda alla session-states direkt

    app_mode, page = sidebar_layout()
        
#region DIARY    
    df = st.session_state[app_mode.lower()]

    if page == "Dashboard":
        col1, col2, col3 = st.columns(3)

        # DARK SIDE
        with col1:
            with st.container():
                if app_mode == "Diary":
                    col="activity"
                    kpi_col="weekday"
                    kpi_str="Worst Day"
                    subheader_txt="This made you feel shitty.."
                if app_mode == "News":
                    col="title"
                    kpi_col="news_section"
                    kpi_str="Worst Section"
                    subheader_txt="War and insanity!"
                    
                st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                
                mood = "Negativt"
                st.header("DARK SIDE")
                st.divider()
                st.subheader(subheader_txt)
                
                activities = show_activities(df, mood, column=col)
                
                # skriv ut varje rad för sig
                for activity in activities:
                    st.markdown(f"🔴 **{activity}**")
                                                                
                st.divider()
                
                # --- KPIS ---
                percentage, worst_day, streak = show_kpis(df, mood, column=kpi_col)
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                with col_kpi1:
                    st.metric("Percentage", percentage)
                with col_kpi2:
                    st.metric(kpi_str, worst_day)
                with col_kpi3:
                    st.metric("Longest Streak", f"{streak} days")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if app_mode == "Diary":
                    # knappen genererar text o sparar i session_state
                    if st.button("Hit for guidance!", key="btn_neg"):
                        st.session_state.neg_guidance_text = give_helpful_advices(df, mood, column="activity")
                    if st.session_state.neg_guidance_text:
                        st.markdown(st.session_state.neg_guidance_text)

        # PROMPT OCH AUDIO
        with col2:
            col_2(app_mode)
                                
        # HAPPY PLACE    
        with col3:
            with st.container():
                if app_mode == "Diary":
                    col="activity"
                    kpi_col="weekday"
                    kpi_str="Best Day"
                    subheader_txt="Stick to the good stuff!"
                if app_mode == "News":
                    col="title"
                    kpi_col="news_section"
                    kpi_str="Best Section"
                    subheader_txt="Lollipops and unicorns!"
                    
                st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
                
                st.header("HAPPY PLACE")
                
                st.divider()
                
                st.subheader(subheader_txt)
                
                mood = "Positivt"
                
                activities = show_activities(df, mood, column=col)
                
                for activity in activities:
                    st.markdown(f"🟢 **{activity}**")
                
                st.divider()
                
                # --- KPIS ---
                percentage, best_day, streak = show_kpis(df, mood, column=kpi_col)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Percentage", percentage)
                with c2:
                    st.metric(kpi_str, best_day)
                with c3:
                    st.metric("Longest Streak", f"{streak} days")
                    
                st.markdown('</div>', unsafe_allow_html=True)
                if app_mode == "Diary":
                    # Generera och spara
                    if st.button("Smash for cash!?", key="btn_pos"):
                        st.session_state.pos_guidance_text = give_helpful_advices(df, mood, column="activity")
                    # Visa
                    if st.session_state.pos_guidance_text:
                        st.markdown(st.session_state.pos_guidance_text)
                
    
    # STATS
    elif page == "Stats":
        if app_mode == "Diary":
            df = update_diary()
        
        current_df = df.sort_values(by="date", ascending=False)    
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Bad Triggers")
            negative_triggers = plot_negative_triggers(current_df)
            st.plotly_chart(negative_triggers)
        
        with col2:
            st.subheader("Pos. vs Neg. Keywords")
            keywords_sunburst = plot_keyword_sunburst(current_df)
            st.plotly_chart(keywords_sunburst)
            
        # Line plot som visar mood över tid
        if app_mode == "Diary":
            st.markdown("### Måendeöversikt över tid")
            line_plot_mood = timeline_plot(current_df, "mood")
        if app_mode == "News":
            st.markdown("### Scatter of news sections")
            line_plot_mood = scatter_plot(current_df, "count", "news_section") 
        st.plotly_chart(line_plot_mood)       
        
        keyword_plot=plot_combined_triggers(current_df)
        st.plotly_chart(keyword_plot)
        
    # READ DIARY    
    elif page == f"Read {app_mode}":  
        if app_mode == "Diary":
            df = update_diary()
            current_df = df.copy()
        if app_mode == "News":
            current_df = df.copy()
            current_df["date"] = pd.to_datetime(current_df["date"])
            current_df["weekday"] = current_df["date"].dt.day_name()
            
        current_df = current_df.sort_values(by="date", ascending=False)

                    
        col1, col2 = st.columns(2)
        with col1:
            st.header(app_mode)
            st.dataframe(current_df, hide_index=True)
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            # Pie plot som visar mood över veckodagarna
            pie_plot_mood_weekdays = pie_plot(current_df, current_df['weekday'], current_df['mood'])
            st.plotly_chart(pie_plot_mood_weekdays)
        


if __name__ == "__main__":
    layout()