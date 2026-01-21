import os
import streamlit as st
import requests

BACKEND_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


input = st.text_input(label = "Vad undrar du?")

if input:
    answer=requests.post(f"{BACKEND_BASE_URL}/query", json={"prompt": input})
    
    st.write(answer.json())