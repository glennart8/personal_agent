import os
import streamlit as st
import requests
# from pa_agent.src.pa_agent.backend.speech_to_text import get_devices, record_audio, transcribe_audio
from pathlib import Path

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


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