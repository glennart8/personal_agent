import os
import streamlit as st
import requests
from css import get_css
import base64
from plots import pie_plot, plot_keyword_sunburst, plot_negative_triggers, plot_combined_triggers, timeline_plot, scatter_plot
from utils import load_data, show_activities, give_helpful_advices, show_kpis, show_trend, init_state, update_diary, SUGGESTIONS_NEWS, SUGGESTIONS_DIARY, BACKEND_BASE_URL


get_css()

     
def layout():
    init_state() # Ladda alla session-states direkt

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
            menu = ["Dashboard", "Stats", "News"]

        page = st.radio(
            "Välj sida:",
            menu,
            label_visibility="collapsed"
        )
        
        show_trend(df)
        
#region DIARY    
  
    if app_mode == "Diary":

        df = st.session_state["diary"]

        if page == "Dashboard":
            col1, col2, col3 = st.columns(3)

            # DARK SIDE
            with col1:
                with st.container():
                    st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                    
                    st.header("DARK SIDE")
                    st.divider()
                    st.subheader("This made you feel shitty..")
                    
                    mood = "Negativt"
                    activities = show_activities(df, mood, column="activity")
                    
                    # skriv ut varje rad för sig
                    for activity in activities:
                        st.markdown(f"🔴 **{activity}**")
                                                                    
                    st.divider()
                    
                    # --- KPIS ---
                    percentage, worst_day, streak = show_kpis(df, mood, column="weekday")
                    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                    with col_kpi1:
                        st.metric("Percentage", percentage)
                    with col_kpi2:
                        st.metric("Worst Day", worst_day)
                    with col_kpi3:
                        st.metric("Longest Streak", f"{streak} days")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # knappen genererar text o sparar i session_state
                    if st.button("Hit for guidance!", key="btn_neg"):
                        st.session_state.neg_guidance_text = give_helpful_advices(df, mood, column="activity")
                    
                    if st.session_state.neg_guidance_text:
                        st.markdown(st.session_state.neg_guidance_text)

            # PROMPT OCH AUDIO
            with col2:
                # Centrerad rubrik och mer marginal, padding elelr va fan det hter mellan ljud o knapp
                st.markdown("""
                    <h2 style='text-align: center; margin-bottom: 0; color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>
                        the dAgent
                    </h2>
                    <hr style='margin: 10px 0 30px 0; opacity: 0.3;'> 
                """, unsafe_allow_html=True) 

                # Skriv ut gammal historik FÖRST 
                for message in st.session_state.messages_diary:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                chat_input_choice = st.chat_input("Just tell me dude..")
                
                # Visa pills
                selected_pill = st.pills(
                    "Förslag",
                    options=SUGGESTIONS_DIARY.keys(), # sport, bilar osv
                    label_visibility="collapsed",
                    selection_mode="single",
                    key="news_pills"
                )
                
                # Om man skrivit i rutan gäller det, annars kollar vi om man klickat på en pill
                prompt = None
                
                if chat_input_choice:
                    prompt = chat_input_choice
                elif selected_pill:
                    # hämta value från suggestions
                    prompt = SUGGESTIONS_DIARY[selected_pill]
                
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
                            response = requests.post(f"{BACKEND_BASE_URL}/transcribe/diary", files=files)
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
                    # spara frågan direkt
                    st.session_state.messages_diary.append({"role": "user", "content": prompt})

                    # skriv ut frågan direkt - snyggare UX 
                    with st.chat_message("user"):
                        st.write(prompt)

                    with st.spinner("Thinking..."):
                        try:
                            response = requests.post(f"{BACKEND_BASE_URL}/text_input/diary", json={"prompt": prompt})
                            if response.status_code == 200:
                                data = response.json()
                                
                                answer_text = data["text_output"]
                                
                                # spara svaret i historiken
                                st.session_state.messages_diary.append({"role": "assistant", "content": answer_text})
                                
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
                                    
            # HAPPY PLACE    
            with col3:
                with st.container():
                    st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
                    
                    st.header("HAPPY PLACE")
                    
                    st.divider()
                    
                    st.subheader("Stick to the good stuff!")
                    mood = "Positivt"
                    activities = show_activities(df, mood, column="activity")
                    
                    for activity in activities:
                        st.markdown(f"🟢 **{activity}**")
                    
                    st.divider()
                    
                    # --- KPIS ---
                    percentage, best_day, streak = show_kpis(df, mood, column="weekday")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Percentage", percentage)
                    with c2:
                        st.metric("Best Day", best_day)
                    with c3:
                        st.metric("Longest Streak", f"{streak} days")

                    # Generera och spara
                    if st.button("Smash for cash!?", key="btn_pos"):
                        st.session_state.pos_guidance_text = give_helpful_advices(df, mood, column="activity")
                    
                    # Visa
                    if st.session_state.pos_guidance_text:
                        st.markdown(st.session_state.pos_guidance_text)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # STATS
        elif page == "Stats":
            df = update_diary()
            
            diary_df = df.sort_values(by="date", ascending=False)    
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top Bad Triggers")
                negative_triggers = plot_negative_triggers(diary_df)
                st.plotly_chart(negative_triggers)
            
            with col2:
                st.subheader("Pos. vs Neg. Keywords")
                keywords_sunburst = plot_keyword_sunburst(diary_df)
                st.plotly_chart(keywords_sunburst)
                
            # Line plot som visar mood över tid
            st.markdown("### Måendeöversikt över tid")
            line_plot_mood = timeline_plot(diary_df, "mood")
            st.plotly_chart(line_plot_mood)       
            
            keyword_plot=plot_combined_triggers(diary_df)
            st.plotly_chart(keyword_plot)
            
        # READ DIARY    
        elif page == "Read Diary":  
            df = update_diary()
                      
            col1, col2 = st.columns(2)
            with col1:
                st.header("Diary")
                diary_df = df.sort_values(by="date", ascending=False)
                st.dataframe(diary_df)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                # Pie plot som visar mood över veckodagarna
                pie_plot_mood_weekdays = pie_plot(diary_df, diary_df['weekday'], diary_df['mood'])
                st.plotly_chart(pie_plot_mood_weekdays)
#region NEWS

    # NEWS
    elif app_mode == "News":
        
        df = st.session_state["news"]

        if page == "Dashboard":
            col1, col2, col3 = st.columns(3)

            # DARK SIDE
            with col1:
                with st.container():
                    st.markdown('<div class="dark-side-bg">', unsafe_allow_html=True)
                    st.header("DARK SIDE")
                    
                    st.divider()    
                    st.subheader("War and insanity!")

                    mood = "Negativt" # LITET NNNNNN
                    activities = show_activities(df, mood, column="title")
                    
                    # skriv ut varje rad för sig
                    for activity in activities:
                        st.markdown(f"🔴 **{activity}**")                                         

                    st.divider()
                    
                    # --- KPIS ---
                    percentage, best_day, streak = show_kpis(df, mood, column="news_section")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Percentage", percentage)
                    with c2:
                        st.metric("Worst Section", best_day)
                    with c3:
                        st.metric("Longest Streak", f"{streak} days")

        
                    st.markdown('</div>', unsafe_allow_html=True)

            # PROMPT OCH AUDIO
            with col2:
                # Centrerad rubrik och mer marginal, padding elelr va fan det hter mellan ljud o knapp
                st.markdown("""
                    <h2 style='text-align: center; margin-bottom: 0; color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>
                        the dAgent
                    </h2>
                    <hr style='margin: 10px 0 30px 0; opacity: 0.3;'> 
                """, unsafe_allow_html=True) 

                # Skriv ut gammal historik FÖRST 
                for message in st.session_state.messages_news:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                chat_input_choice = st.chat_input("Just tell me dude..")
                                             
                # Visa "Pills" (Knapparna)
                selected_pill = st.pills(
                    "Förslag",
                    options=SUGGESTIONS_NEWS.keys(), # sport, bilar osv
                    label_visibility="collapsed",
                    selection_mode="single",
                    key="news_pills"
                )
                
                # Om man skrivit i rutan gäller det, annars kollar vi om man klickat på en pill
                prompt = None
                
                if chat_input_choice:
                    prompt = chat_input_choice
                elif selected_pill:
                    # hämta value - den långa frågan baserat på key
                    prompt = SUGGESTIONS_NEWS[selected_pill]

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
                            response = requests.post(f"{BACKEND_BASE_URL}/transcribe/news", files=files)
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
                            response = requests.post(f"{BACKEND_BASE_URL}/text_input/news", json={"prompt": prompt})
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

            # HAPPY PLACE
            with col3:
                 with st.container():
                    st.markdown('<div class="happy-place-bg">', unsafe_allow_html=True)
                    st.header("HAPPY PLACE")

                    st.divider()
                    
                    st.subheader("Lollipops and unicorns!")
                    mood = "Positivt"
                    activities = show_activities(df, mood, column="title")
                    
                    for activity in activities:
                        st.markdown(f"🟢 **{activity}**")
                    
                    st.divider()       
                  
                    # --- KPIS ---
                    percentage, best_day, streak = show_kpis(df, mood, column="news_section")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Percentage", percentage)
                    with c2:
                        st.metric("Best Section", best_day)
                    with c3:
                        st.metric("Longest Streak", f"{streak} days")   


                    st.markdown('</div>', unsafe_allow_html=True)

        elif page == "Stats":
            # Visa plots för nyheter
            news_df = df.sort_values(by="date", ascending=False)  
            # raw_url = "https:\/\/gfx.omni.se\/images\/9eea82fc-83c2-4c09-b877-b44728567cda?h=708&tight=false&w=1372"  
            # clean_url = raw_url.replace(r"\/", "/")
            # st.image(clean_url)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top Bad Triggers")
                negative_triggers = plot_negative_triggers(news_df)
                st.plotly_chart(negative_triggers)
            
            with col2:
                st.subheader("Pos. vs Neg. Keywords")
                keywords_sunburst = plot_keyword_sunburst(news_df)
                st.plotly_chart(keywords_sunburst)
                
            # Line plot som visar mood över tid
            st.markdown("### Scatter of news sections")
            line_plot_mood = scatter_plot(news_df, "count", "news_section") 
            st.plotly_chart(line_plot_mood)       
            
            keyword_plot=plot_combined_triggers(news_df)
            st.plotly_chart(keyword_plot)
            pass

        elif page == "News":
            news_df = df.sort_values(by="date", ascending=False)  
            
            col1, col2 = st.columns(2)
            with col1:
                st.header("Diary")
                diary_df = df.sort_values(by="date", ascending=False)
                st.dataframe(diary_df)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                # Pie plot som visar mood över veckodagarna
                import pandas as pd
                df_date = news_df.copy()
                df_date["date"] = pd.to_datetime(df_date["date"])
                df_date["weekday"] = df_date["date"].dt.day_name()
                pie_plot_mood_weekdays = pie_plot(df_date, df_date['weekday'], df_date['mood'])
                st.plotly_chart(pie_plot_mood_weekdays)
#endregion

if __name__ == "__main__":
    layout()