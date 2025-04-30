import streamlit as st
import json
import os
import uuid
from datetime import datetime

def load_css():
    """Load custom CSS for child-friendly visuals"""
    css = """
    <style>
        /* Overall theme */
        .stApp {
            background-color: #FFFAFA;  /* dark slate blue */
            font-family: 'Comic Sans MS', 'Marker Felt', fantasy;
        }
        
        /* Welcome page */
        .welcome-container {
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .welcome-text {
            font-size: 3rem;
            color: #4b89dc;
            margin-bottom: 0;
        }
        
        .intro-text {
            font-size: 1.3rem;
            text-align: center;

            color: #666;
            margin-top: 0;
        }
        
        /* Logo animation */
        .welcome-animation {
            height: 180px;
            position: relative;
            margin-bottom: 10px;
        }
        
        .logo-container {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }
        
        .logo-icon {
            position: absolute;
            font-size: 60px;
            top: 25px;
            left: 30px;
            animation: pulse 3s infinite;
        }
        
        .items {
            position: absolute;
            width: 100%;
            height: 100%;
            animation: rotate 15s linear infinite;
        }
        
        .item {
            position: absolute;
            font-size: 30px;
        }
        
        .item:nth-child(1) {
            top: 0;
            left: 45px;
            animation: bounce 2s infinite;
        }
        
        .item:nth-child(2) {
            bottom: 0;
            right: 10px;
            animation: bounce 2.3s infinite;
        }
        
        .item:nth-child(3) {
            bottom: 0;
            left: 10px;
            animation: bounce 1.7s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        /* Game interface */
        .game-title {
            text-align: center;
            color: #4b89dc;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .player-info {
            text-align: center;
            color: #666;
            font-size: 1.2rem;
            margin-top: 0;
        }
        
        .current-item-container {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background-color: #fff;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .current-item {
            color: #4b89dc;
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .food-item {
            font-size: 4rem;
            margin: 20px 0;
        }
        
        .baskets-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin: 30px 0;
        }
        
        .basket-label {
            text-align: center;
            font-size: 1.3rem;
            color: #555;
            margin-bottom: 10px;
        }
        
        /* Dashboard styles */
        .dashboard-title {
            color: #4b89dc;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .insight-card {
            background-color: #fff;
            border-left: 5px solid #4b89dc;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .insight-note {
            color: #888;
            font-size: 0.9rem;
            font-style: italic;
            margin-top: 20px;
        }
        
        .stats-container {
            text-align: center;
            margin-top: 20px;
            font-size: 1.1rem;
            color: #666;
        }
        
        /* Override Streamlit button styles */
        .stButton > button {
            background-color: #4b89dc;
            color: white;
            border-radius: 25px;
            border: none;
            padding: 10px 24px;
            font-family: 'Comic Sans MS', 'Marker Felt', fantasy;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: #3a7bd5;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .child-info-card {
            background: #fffdf7;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            max-width: 500px;
            margin: 0 auto;
            font-family: 'Comic Sans MS', 'Marker Felt', fantasy;
        }

        .child-info-card h3 {
            text-align: center;
            color: #4b89dc;
            margin-bottom: 10px;
        }

        .input-row {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }

        .input-column {
            flex: 1;
        }

        .voice-toggle {
            margin-top: 10px;
            text-align: center;
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def save_session_data(response_data):
    """Save session data to a JSON file"""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Create a filename based on session ID
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    filename = f"data/session_{st.session_state.session_id}.json"
    
    # Read existing data or create new list
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = []
    except json.JSONDecodeError:
        data = []
    
    # Add new response data
    if isinstance(data, list):
        data.append(response_data)
    else:
        data = [response_data]
    
    # Write updated data back to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)