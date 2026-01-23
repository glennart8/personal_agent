import os
import streamlit as st
import requests
from speech_to_text import get_devices, record_audio, transcribe_audio
from pathlib import Path

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# AUDIO_PATH = Path(__file__).parents[0] / "recording.wav"

# input = st.text_input(label = "Vad undrar du?")

# if input:
#     answer=requests.post(f"{BACKEND_BASE_URL}/query", json={"prompt": input})
    
#     st.write(answer.json())
    
    
def layout():
    # input_info = get_devices()
    # output_info = get_devices("output")
    # # st.write(output_info)
    
    # name = input_info["name"]
    # output_name = output_info["name"]
    
    # id = int(input_info["index"])
    # samplerate = int(input_info["default_samplerate"])
    # channels = int(input_info["max_input_channels"])
    
    # st.write(f"Input device: {name}")
    # st.write(f"Output device: {output_name}")
    
    # if st.button("Record Audio"):
    #     transcription = record_audio(AUDIO_PATH, samplerate, id, channels)
        
    #     st.write(transcription)
    
    audio = st.audio_input("Record")
    if audio:
        text = transcribe_audio(audio)
        st.write(text)
        requests.post(f"{BACKEND_BASE_URL}/add_text", json={"prompt": text})


if __name__ == "__main__":
    layout()