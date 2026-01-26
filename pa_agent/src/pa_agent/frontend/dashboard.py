import os
import streamlit as st
import requests
import base64


BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

audio = st.audio_input("Record")
chat_input = st.chat_input()
if audio:
    # text = transcribe_audio(audio)
    files = {"file": ("recording.wav", audio, "audio/wav")}
    # st.write(text)
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