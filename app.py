import streamlit as st
import time
from datetime import datetime
import pandas as pd
import altair as alt
import json
import os
import uuid

# Import from our modules
from child_game import show_game_interface, init_game_state
from parent_dashboard import show_parent_dashboard
from utils import load_css, save_session_data
from game_data import FOOD_CATEGORIES, ADVANCED_CATEGORIES

# Set page configuration
st.set_page_config(
    page_title="SmartSort Kids - Learn & Play!",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS for child-friendly visuals
load_css()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.page = 'welcome'
    st.session_state.mode = 'child'  # Default mode is child
    st.session_state.child_name = ''
    st.session_state.child_age = '5'
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.parent_password = None
    
    # Initialize game state
    init_game_state()

def show_welcome_page():
    """Display the welcome page with mode selection and child info"""
    
    #st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    
    # Animated logo
    st.markdown("""
    <div class='welcome-animation'>
        <div class='logo-container'>
        <div class='logo-icon'>🧠</div>
        <div class='items'>
            <span class='item'>🍎</span>
            <span class='item'>🍌</span>
            <span class='item'>🍩</span>
            <span class='item'>🧃</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center;'><h1 class='welcome-text'>Know Your Food!</h1></div>", unsafe_allow_html=True)
    st.markdown("<p class='intro-text'>Learn about food groups through fun sorting games!</p>", unsafe_allow_html=True)
    
    # Create tabs for child and parent modes
    tabs = st.tabs(["👶 Child Mode", "👨‍👩‍👧 Parent Mode"])
    
    # Child mode tab
    with tabs[0]:
        st.markdown("<div style='text-align: center;'><h3>👶 Child Information</h3>", unsafe_allow_html=True)
        



        #st.markdown("<div class='child-info-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Let's Get Started!</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4 style='color:#4b89dc;'>👤 Your Name</h4>", unsafe_allow_html=True)
            name = st.text_input("", key="name_input", placeholder="Type here...", max_chars=15)

        with col2:
            age_options = ["3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
            st.markdown("<h4 style='color:#4b89dc;'>🎂 Your Age</h4>", unsafe_allow_html=True)
            age = st.selectbox("", age_options, index=2)

        st.markdown("<div class='voice-toggle'>", unsafe_allow_html=True)
        use_voice = st.checkbox("🔊 Enable Voice Features", value=False,help="Turn on speaking and listening")
        st.markdown("</div></div>", unsafe_allow_html=True)

        
        # Start button
        if st.button("Start Playing! 🚀", key="start_button"):
            if name:
                st.session_state.child_name = name
                st.session_state.child_age = ["3", "4", "5", "6", "7"][age_options.index(age)]
                st.session_state.use_voice = use_voice
                st.session_state.mode = 'child'
                st.session_state.page = 'game'
                st.experimental_rerun()
            else:
                st.warning("Please tell us your name first!")
    
    # Parent mode tab
    with tabs[1]:
        st.markdown("<h3>👨‍👩‍👧 Parent Access</h3>", unsafe_allow_html=True)
        
        # Simple password protection
        if 'parent_authenticated' not in st.session_state:
            st.session_state.parent_authenticated = False
            
        if not st.session_state.parent_authenticated:
            password = st.text_input("Parent Password", type="password", 
                                    placeholder="Enter password to view analytics",
                                    help="Default password is 'parent123'")
            
            if st.button("Log In", key="parent_login"):
                # Very simple authentication - in real app would be more secure
                if password == "parent123":
                    st.session_state.parent_authenticated = True
                    st.session_state.mode = 'parent'
                    st.experimental_rerun()
                else:
                    st.error("Incorrect password")
        else:
            st.success("Authenticated as parent")
            if st.button("View Dashboard", key="view_dashboard"):
                st.session_state.mode = 'parent'
                st.session_state.page = 'dashboard'
                st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main app function
def main():
    # Sidebar: About this App
    with st.sidebar:
        st.markdown("## 📘 About SmartSort Kids")

        st.sidebar.image("instructions.png", use_column_width=True)

        st.markdown("---")

        st.markdown("### 🔗 Connect with Me")
        st.markdown("""
        [![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/sahilkoul123/)  | [![GitHub](https://img.shields.io/badge/GitHub-black?logo=github&style=flat)](https://koulmesahil.github.io/)
        """, unsafe_allow_html=True)
        st.markdown("---")



    # Add a small button in the top corner to switch modes
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.session_state.mode == 'child' and st.session_state.page != 'welcome':
            if st.button("👨‍👩‍👧", help="Parent Mode"):
                
                st.session_state.page = 'welcome'

                show_welcome_page()
                st.experimental_rerun()  # Simple password

        elif st.session_state.mode == 'parent' and st.session_state.page != 'welcome':
            if st.button("👶", help="Child Mode"):
                st.session_state.page = 'welcome'

                show_welcome_page()
                st.experimental_rerun()

    
    # Display appropriate content based on mode and page
    if st.session_state.page == 'welcome':
        show_welcome_page()
    elif st.session_state.mode == 'child' and st.session_state.page == 'game':
        show_game_interface()
    elif st.session_state.mode == 'parent' and st.session_state.page == 'dashboard':
        if st.session_state.parent_authenticated:
            show_parent_dashboard()
        else:
            st.error("Authentication required")
            st.session_state.page = 'welcome'
            st.experimental_rerun()
    else:
        show_welcome_page()  # Default fallback

if __name__ == "__main__":
    main()