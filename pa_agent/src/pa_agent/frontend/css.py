import streamlit as st

def get_css():
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
        
        [sidebar="stSidebar"] > div:first-child {
        width: 200px;
        }
        
        .stApp {
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                            url("https://images.unsplash.com/photo-1596820286510-1783d01bdaae?q=80&w=1199&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }
        
        
        .happy-place-bg {
            background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), 
                            url("https://images.unsplash.com/photo-1617078881078-39b6071a1c4a?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            padding: 20px;
            border-radius: 10px;
            border: 0.5px solid #ddd;
            color: white;
            min-height: 100px;
        }
        
        
        .dark-side-bg {
            background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), 
                            url("https://images.unsplash.com/photo-1583459094467-e0db130c0dea?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            padding: 20px;
            border-radius: 10px;
            border: 0.5px solid #ddd;
            color: white;
            min-height: 100px;
        }
        
        </style>
    """, unsafe_allow_html=True)