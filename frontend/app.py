import streamlit as st
import requests

input = st.text_input(label = "Vad undrar du?")

if input:
    answer=requests.post("http://localhost:8000/query", json={"prompt": input})
    
    st.write(answer.json())