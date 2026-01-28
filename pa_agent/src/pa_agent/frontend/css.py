import streamlit as st

def get_css():
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
        
        section[data-testid="stSidebar"] {
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.6)), 
                            url("https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
        }
        
        .stApp {
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                            url("https://images.unsplash.com/photo-1596820286510-1783d01bdaae?q=80&w=1199&auto=format&fit=crop");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }
        
        .happy-place-bg {
            /* Ljusare toning (0.2) och kanske en touch av varmt ljus */
            background-image: linear-gradient(rgba(0, 50, 0, 0.3), rgba(0, 0, 0, 0.3)), 
                            url("https://images.unsplash.com/photo-1617078881078-39b6071a1c4a?q=80&w=687&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            padding: 25px;
            border-radius: 15px;
            color: white;
            min-height: 100%;
            
            border: 2px solid #4CAF50; 
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.3); 
        }
        
        .dark-side-bg {
            /* Mörkare toning (0.6) för att göra det dunkelt */
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(50, 0, 0, 0.6)), 
                            url("https://images.unsplash.com/photo-1583459094467-e0db130c0dea?q=80&w=687&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            padding: 25px;
            border-radius: 15px;
            color: white;
            min-height: 100%;
            
            border: 2px solid #D32F2F; 
            box-shadow: 0 0 20px rgba(211, 47, 47, 0.3); 
        }
        
        .kpi-container {
            border-top: 1px solid rgba(255,255,255,0.2);
            margin-top: 20px;
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
        }
        
        .stTextInput input {
            background-color: rgba(0,0,0,0.3) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: red !important;       
            caret-color: red;            
        }
        
        
        </style>
    """, unsafe_allow_html=True)