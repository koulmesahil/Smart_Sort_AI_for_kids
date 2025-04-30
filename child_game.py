import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import json
import os
from utils import save_session_data


# This will be imported from game_data.py
# For reference only:
# FOOD_CATEGORIES = {
#     "Fruits": ["🍎 Apple", "🍌 Banana", "🍊 Orange", "🍓 Strawberry", "🍇 Grapes", "🍉 Watermelon"],
#     "Vegetables": ["🥕 Carrot", "🥦 Broccoli", "🍅 Tomato", "🥬 Lettuce", "🥒 Cucumber", "🌽 Corn"],
#     "Dairy": ["🧀 Cheese", "🥛 Milk", "🍦 Ice Cream", "🧈 Butter", "🥄 Yogurt"],
#     "Grains": ["🍞 Bread", "🥣 Cereal", "🍝 Pasta", "🍚 Rice", "🥯 Bagel"],
#     "Protein": ["🥚 Egg", "🥜 Peanuts", "🍗 Chicken", "🐟 Fish", "🥩 Meat"]
# }

# ADVANCED_CATEGORIES = {
#     "Healthy": ["🍎 Apple", "🥕 Carrot", "🥦 Broccoli", "🥒 Cucumber", "🥬 Lettuce", "🥛 Milk", "🥚 Egg"],
#     "Sometimes Foods": ["🍦 Ice Cream", "🍩 Donut", "🍪 Cookie", "🍫 Chocolate", "🍕 Pizza"]
# }

def init_game_state():
    """Initialize the game state in the session"""
    # Game settings
    if 'game_level' not in st.session_state:
        st.session_state.game_level = 1
    if 'current_categories' not in st.session_state:
        st.session_state.current_categories = ["Fruits", "Vegetables"]  # Start with two categories
    if 'current_item' not in st.session_state:
        st.session_state.current_item = None
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = "standard"  # standard or advanced
    if 'items_per_level' not in st.session_state:
        st.session_state.items_per_level = 5
    if 'items_sorted' not in st.session_state:
        st.session_state.items_sorted = 0
    
    # Performance tracking
    if 'correct_sorts' not in st.session_state:
        st.session_state.correct_sorts = 0
    if 'incorrect_sorts' not in st.session_state:
        st.session_state.incorrect_sorts = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    if 'response_times' not in st.session_state:
        st.session_state.response_times = []
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    if 'confusion_matrix' not in st.session_state:
        st.session_state.confusion_matrix = {}

def get_next_item(from_categories=None):
    """Get a random food item from specified categories"""
    from game_data import FOOD_CATEGORIES, ADVANCED_CATEGORIES
    
    # Determine which categories to use
    if from_categories is None:
        from_categories = st.session_state.current_categories
    
    # Get all items from the selected categories
    all_items = []
    categories_dict = FOOD_CATEGORIES if st.session_state.game_mode == "standard" else ADVANCED_CATEGORIES
    
    for category in from_categories:
        if category in categories_dict:
            all_items.extend([(item, category) for item in categories_dict[category]])
    
    # Pick a random item
    if all_items:
        item, category = random.choice(all_items)
        return item, category
    else:
        return "🍽️ Food Item", "Unknown"  # Fallback

def check_answer(item, selected_category):
    """Check if the food item belongs to the selected category"""
    from game_data import FOOD_CATEGORIES, ADVANCED_CATEGORIES
    
    categories_dict = FOOD_CATEGORIES if st.session_state.game_mode == "standard" else ADVANCED_CATEGORIES
    
    for category, items in categories_dict.items():
        if item in items and category == selected_category:
            return True
    return False

def record_response(item, correct_category, selected_category, is_correct, response_time):
    """Record the child's response for analytics"""
    # Add to session history
    response_data = {
        "timestamp": datetime.now().isoformat(),
        "item": item,
        "correct_category": correct_category,
        "selected_category": selected_category,
        "is_correct": is_correct,
        "response_time": response_time,
        "level": st.session_state.game_level,
        "child_name": st.session_state.child_name,
        "child_age": st.session_state.child_age
    }
    
    st.session_state.session_history.append(response_data)
    
    # Update confusion matrix
    confusion_key = f"{correct_category}:{selected_category}"
    if confusion_key not in st.session_state.confusion_matrix:
        st.session_state.confusion_matrix[confusion_key] = 0
    st.session_state.confusion_matrix[confusion_key] += 1
    
    # Save to file
    save_session_data(response_data)
    
    # Update counters
    st.session_state.items_sorted += 1
    if is_correct:
        st.session_state.correct_sorts += 1
    else:
        st.session_state.incorrect_sorts += 1
    
    # Record response time
    st.session_state.response_times.append(response_time)
    
    # Check if level should increase
    if (st.session_state.items_sorted % st.session_state.items_per_level == 0 and 
        st.session_state.correct_sorts / max(1, st.session_state.items_sorted) > 0.7):
        increase_difficulty()

def increase_difficulty():
    """Make the game harder based on child's performance"""
    from game_data import FOOD_CATEGORIES
    
    # Increase level
    st.session_state.game_level += 1
    
    # Add more categories as the child progresses
    if st.session_state.game_level == 2 and "Dairy" not in st.session_state.current_categories:
        st.session_state.current_categories.append("Dairy")
    elif st.session_state.game_level == 3 and "Grains" not in st.session_state.current_categories:
        st.session_state.current_categories.append("Grains")
    elif st.session_state.game_level == 4 and "Protein" not in st.session_state.current_categories:
        st.session_state.current_categories.append("Protein")
    elif st.session_state.game_level >= 5:
        # At level 5+, switch to advanced categories if all standard ones are mastered
        if st.session_state.correct_sorts / max(1, st.session_state.items_sorted) > 0.85:
            st.session_state.game_mode = "advanced"
            st.session_state.current_categories = ["Healthy", "Sometimes Foods"]

def text_to_speech(text):
    """Use browser TTS to speak text to the child"""
    if 'use_voice' in st.session_state and st.session_state.use_voice:
        # Create a hidden component with speech synthesis
        js_code = f"""
        <script>
            function speak() {{
                const utterance = new SpeechSynthesisUtterance("{text}");
                utterance.rate = 0.9;  // Slightly slower for children
                utterance.pitch = 1.1; // Slightly higher pitch for child-friendly voice
                speechSynthesis.speak(utterance);
            }}
            speak();
        </script>
        """
        st.components.v1.html(js_code, height=0)

def show_game_interface():
    """Display the main game interface for children"""
    st.markdown(f"<h1 class='game-title'>SmartSort Kids - Level {st.session_state.game_level}</h1>", unsafe_allow_html=True)
    
    # Display child's name and progress
    st.markdown(f"<p class='player-info'>Player: {st.session_state.child_name} (Age {st.session_state.child_age})</p>", unsafe_allow_html=True)
    
    
    

    st.markdown("""
        <div class='stats-container' style='text-align: center; padding: 10px; 
            background: #fff7e6; border-radius: 15px; border: 2px dashed #f4c542; 
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1); font-size: 1.2rem;'>
            <p>🧺 <b>Items Sorted:</b> <span style='color: #4b89dc;'>{items}</span> &nbsp;|&nbsp;
            ✅ <b>Correct:</b> <span style='color: #28a745;'>{correct}</span> &nbsp;|&nbsp;
            🌟 <b>Score:</b> <span style='color: #f39c12;'>{score}</span></p>
        </div>
    """.format(items=st.session_state.items_sorted,
            correct=st.session_state.correct_sorts,
            score=st.session_state.correct_sorts * 10),
    unsafe_allow_html=True)

    
    # Select item if none is selected
    if st.session_state.current_item is None:
        item, correct_category = get_next_item()
        st.session_state.current_item = item
        st.session_state.correct_category = correct_category
        st.session_state.item_start_time = time.time()
        
        # Speak the item name for young children
        if st.session_state.child_age in ["3", "4", "5"]:
            text_to_speech(f"Where does {item.split(' ')[1]} go?")
    
    # Display the current item
    #st.markdown("<div class='current-item-container'>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .center-wrapper {
            text-align: center;
            margin-top: 1rem;
        }
        .current-item {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .food-item {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='center-wrapper'>
            <h2 class='current-item'>Where does this go?</h2>
            <div class='food-item'>{st.session_state.current_item}</div>
        </div>
    """, unsafe_allow_html=True)

    
    # Add custom CSS for the baskets
    st.markdown("""
    <style>
        .baskets-container {
            padding: 15px;
            border-radius: 15px;
            background: #f8f9fa;
            margin-bottom: 20px;
        }
        .basket-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 15px 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 10px;
            transition: transform 0.3s;
            cursor: pointer;
            border: 3px solid #e0e0e0;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .basket-card:hover {
            transform: scale(1.05);
        }
        .basket-label {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .basket-emoji {
            font-size: 80px;
            margin-bottom: 5px;
            display: block;
        }
        /* Food group specific colors */
        .basket-Fruits {
            background-color: #ffcdd2;
            border-color: #e57373;
        }
        .basket-Vegetables {
            background-color: #c8e6c9;
            border-color: #81c784;
        }
        .basket-Dairy {
            background-color: #e1f5fe;
            border-color: #4fc3f7;
        }
        .basket-Grains {
            background-color: #fff9c4;
            border-color: #fff176;
        }
        .basket-Protein {
            background-color: #f5f5f5;
            border-color: #9e9e9e;
        }
        .basket-Healthy {
            background-color: #e8f5e9;
            border-color: #66bb6a;
        }
        .basket-Sometimes-Foods {
            background-color: #ffe0b2;
            border-color: #ffb74d;
        }
        .hidden-button {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create a container for category baskets
    st.markdown("<div class='baskets-container'>", unsafe_allow_html=True)

    # Define specialized food group emojis
    category_emojis = {
        'Fruits': '🍎',
        'Vegetables': '🥦',
        'Dairy': '🥛',
        'Grains': '🌾',
        'Protein': '🥩',
        'Healthy': '💪',
        'Sometimes Foods': '🍰'
    }

    # Default emoji for categories not in our dictionary
    default_emoji = '🍽️'

    # Create columns for baskets based on current categories
    cols = st.columns(len(st.session_state.current_categories))

    # Display each category basket
    for i, category in enumerate(st.session_state.current_categories):
        with cols[i]:
            # Get appropriate emoji for this category or use default
            category_emoji = category_emojis.get(category, default_emoji)
            
            # Create the category class name (for CSS)
            category_class = category.replace(" ", "-")
            
            # Create a card-like container for each basket
            st.markdown(f"""
            <div class='basket-card basket-{category_class}' id='basket-{i}'>
                <span class='basket-emoji'>{category_emoji}</span>
                <div class='basket-label'>{category}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add the button with the same functionality as before but hidden
            if st.button(f"🧺 Put in {category} 🧺", key=f"basket_{category}", 
                        use_container_width=True, 
                        help=f"Put the {st.session_state.current_item} in the {category} basket"):
                
                # Calculate response time
                response_time = time.time() - st.session_state.item_start_time
                
                # Check if answer is correct
                item = st.session_state.current_item
                correct_category = st.session_state.correct_category
                is_correct = (category == correct_category)
                
                # Record the response
                record_response(item, correct_category, category, is_correct, response_time)
                
                # Give feedback
                if is_correct:
                    st.success(f"Correct! {item.split(' ')[1]} belongs to {category}!")
                    text_to_speech(f"Correct! {item.split(' ')[1]} belongs to {category}!")
                else:
                    st.error(f"Not quite! {item.split(' ')[1]} belongs to {correct_category}.")
                    text_to_speech(f"Not quite! {item.split(' ')[1]} belongs to {correct_category}.")
                
                # Get next item after a short delay
                time.sleep(1.5)
                st.session_state.current_item = None
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Add JavaScript to make the cards clickable
    for i, category in enumerate(st.session_state.current_categories):
        js_safe_category = category.replace("'", "\\'")
        st.markdown(f"""
        <script>
            // Make the basket card clickable
            document.getElementById('basket-{i}').addEventListener('click', function() {{
                // Find the corresponding button and click it
                document.querySelector('button[key="basket_{js_safe_category}"]').click();
            }});
        </script>
        """, unsafe_allow_html=True)
    
# Add a voice command option if enabled
    # Add a voice command option if enabled
    if 'use_voice' in st.session_state and st.session_state.use_voice:
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='color: #6C63FF; font-family: \"Comic Sans MS\", cursive; margin-bottom: 5px;'>Voice Control</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555; font-size: 16px;'>Say: <b>\"Put in [category name]\"</b> or just say the category like <b>\"Fruits\"</b></p>", unsafe_allow_html=True)
            
            # Create a placeholder for voice recognition status
            voice_status = st.empty()
        
        # JavaScript for voice recognition
        voice_js = """
        <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            let isAlwaysListening = true; // Default to true for always listening
            
            // Function to directly click the appropriate category button
            function clickCategoryButton(transcript) {
                const lowerTranscript = transcript.toLowerCase();
                
                // Get all buttons in the document
                const buttons = Array.from(window.parent.document.querySelectorAll('button'));
                
                // Look for buttons that match category patterns
                const categories = ["fruits", "vegetables", "dairy", "grains", "protein", "healthy", "sometimes foods"];
                let buttonClicked = false;
                
                // First try to find exact matches for "Put in X" pattern
                for (const category of categories) {
                    if (lowerTranscript.includes("put in " + category)) {
                        // Find the matching category button
                        const button = buttons.find(btn => 
                            btn.innerText && btn.innerText.toLowerCase().includes("put in " + category)
                        );
                        
                        if (button) {
                            console.log("Clicking button for category:", category);
                            button.click();
                            buttonClicked = true;
                            break;
                        }
                    }
                }
                
                // If no exact match, try just category names
                if (!buttonClicked) {
                    for (const category of categories) {
                        if (lowerTranscript.includes(category)) {
                            // Find the matching category button
                            const button = buttons.find(btn => 
                                btn.innerText && btn.innerText.toLowerCase().includes("put in " + category)
                            );
                            
                            if (button) {
                                console.log("Clicking button for category:", category);
                                button.click();
                                buttonClicked = true;
                                break;
                            }
                        }
                    }
                }
                
                // Update the display element with the result
                if (outputDiv) {
                    if (buttonClicked) {
                        outputDiv.innerHTML = `<span class="feedback-success">🎯 You said: "${transcript}" - Category selected!</span>`;
                    } else {
                        outputDiv.innerHTML = `<span class="feedback-try">🤔 You said: "${transcript}" - Try another category.</span>`;
                    }
                    
                    // Add a fun animation
                    outputDiv.classList.add('pop-in');
                    setTimeout(() => outputDiv.classList.remove('pop-in'), 500);
                }
                
                return buttonClicked;
            }

            // DOM Elements
            let statusIcon;
            let statusText;
            let outputDiv;
            let toggleBtn;

            document.addEventListener('DOMContentLoaded', () => {
                statusIcon = document.getElementById('listeningIcon');
                statusText = document.getElementById('listeningStatus');
                outputDiv = document.getElementById('spokenText');
                toggleBtn = document.getElementById('toggleListenBtn');
                
                // Initialize with always listening
                startContinuousListening();
            });
            
            // Function to update the visual indicator
            function updateListeningStatus(isListening) {
                if (statusIcon) {
                    if (isListening) {
                        statusIcon.innerHTML = '🎤';
                        statusIcon.classList.add('listening-active');
                        if (statusText) statusText.textContent = 'Listening...';
                    } else {
                        statusIcon.innerHTML = '🔇';
                        statusIcon.classList.remove('listening-active');
                        if (statusText) statusText.textContent = 'Paused';
                    }
                }
            }
            
            // Function to restart listening after a short break
            function startContinuousListening() {
                if (isAlwaysListening) {
                    try {
                        recognition.start();
                        updateListeningStatus(true);
                    } catch (e) {
                        // Recognition might already be running, ignore this error
                        console.log("Recognition error:", e);
                    }
                } else {
                    updateListeningStatus(false);
                }
            }

            recognition.onstart = () => {
                updateListeningStatus(true);
            }

            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                
                // Try to click the button directly
                clickCategoryButton(transcript);
                
                // Restart listening after a short delay
                setTimeout(() => {
                    startContinuousListening();
                }, 1000);
            }

            recognition.onend = function() {
                // Restart listening if in always-listening mode
                if (isAlwaysListening) {
                    setTimeout(() => {
                        startContinuousListening();
                    }, 500);
                } else {
                    updateListeningStatus(false);
                }
            }

            recognition.onerror = function(event) {
                if (outputDiv) {
                    if (event.error === 'no-speech') {
                        // Don't show errors for no speech detected
                        console.log("No speech detected");
                    } else {
                        outputDiv.innerHTML = "<span class='feedback-error'>❗ Error: " + event.error + "</span>";
                    }
                }
                
                // Restart after error (except for aborted)
                if (event.error !== 'aborted' && isAlwaysListening) {
                    setTimeout(() => {
                        startContinuousListening();
                    }, 1000);
                }
            }

            // Function to toggle always listening mode
            window.toggleAlwaysListening = function() {
                isAlwaysListening = !isAlwaysListening;
                
                if (toggleBtn) {
                    toggleBtn.textContent = isAlwaysListening ? '🔇 Pause' : '🎤 Start';
                    toggleBtn.className = isAlwaysListening ? 'toggle-button pause' : 'toggle-button start';
                }
                
                if (isAlwaysListening) {
                    startContinuousListening();
                } else {
                    recognition.abort();
                    updateListeningStatus(false);
                }
            }
            
            // Listen for checkbox changes from Streamlit
            window.addEventListener('message', function(event) {
                if (event.data.type === 'streamlit:componentReady') {
                    // Set up a listener for checkbox value changes
                    const observer = new MutationObserver((mutations) => {
                        mutations.forEach((mutation) => {
                            if (mutation.type === 'attributes' && mutation.attributeName === 'data-testid') {
                                // Try to find the checkbox for always listening
                                const checkbox = window.parent.document.querySelector('input[type="checkbox"]');
                                if (checkbox) {
                                    isAlwaysListening = checkbox.checked;
                                    
                                    if (isAlwaysListening) {
                                        startContinuousListening();
                                    } else {
                                        recognition.abort();
                                        updateListeningStatus(false);
                                    }
                                }
                            }
                        });
                    });
                    
                    // Observe the Streamlit app for changes
                    observer.observe(window.parent.document.body, { 
                        attributes: true, 
                        childList: true, 
                        subtree: true 
                    });
                }
            });
        }
        </script>

        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes pop-in {
            0% { transform: scale(0.9); opacity: 0; }
            70% { transform: scale(1.05); opacity: 1; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .pop-in {
            animation: pop-in 0.5s ease forwards;
        }
        
        #voice-control-container {
            font-family: 'Nunito', sans-serif;
            max-width: 400px;
            border-radius: 16px;
            background: linear-gradient(145deg, #f0f0f0, #ffffff);
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        #listening-indicator {
            display: flex;
            align-items: center;
            background: white;
            border-radius: 30px;
            padding: 10px 20px;
            box-shadow: 0 4px 10px rgba(108, 99, 255, 0.1);
            margin-bottom: 15px;
        }
        
        #listeningIcon {
            font-size: 28px;
            margin-right: 10px;
            display: inline-block;
        }
        
        .listening-active {
            animation: bounce 1s infinite;
            color: #6C63FF;
        }
        
        #listeningStatus {
            font-weight: 700;
            font-size: 16px;
            color: #555;
        }
        
        .toggle-button {
            border: none;
            border-radius: 30px;
            padding: 10px 25px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Nunito', sans-serif;
            transition: all 0.3s ease;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .toggle-button.pause {
            background-color: #FF6B6B;
            color: white;
        }
        
        .toggle-button.start {
            background-color: #6C63FF;
            color: white;
        }
        
        .toggle-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }
        
        #spokenText {
            background: white;
            border-radius: 12px;
            padding: 12px;
            min-height: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .feedback-success {
            color: #4CAF50;
            font-weight: 700;
        }
        
        .feedback-try {
            color: #FF9800;
            font-weight: 700;
        }
        
        .feedback-error {
            color: #F44336;
            font-weight: 700;
        }
        
        </style>

        <div id="voice-control-container">
            <div id="listening-indicator">
                <span id="listeningIcon" class="listening-active">🎤</span>
                <span id="listeningStatus">Listening...</span>
            </div>
            
            <button id="toggleListenBtn" onclick="toggleAlwaysListening()" class="toggle-button pause">
                🔇 Pause
            </button>
            
            <div id="spokenText"></div>
        </div>
        """
        
        # Use the HTML component to add voice recognition to column 1
        with col1:
            st.components.v1.html(
                voice_js,
                height=250
            )
        
        # Add fun facts and motivational quotes in column 2
        with col2:

            st.markdown("<h3 style='color: #FF9800; font-family: \"Comic Sans MS\", cursive; margin-bottom: 5px;'>Food Facts & Tips</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #555; font-size: 16px;'>Food powers your body and your brain!</p>", unsafe_allow_html=True)

            # Add CSS for the fact container
            st.markdown("""
            <style>
            .fact-container {
                background: linear-gradient(145deg, #fff4e6, #fffaf0);
                border-radius: 16px;
                padding: 20px;
                margin-top: 10px;
                box-shadow: 0 4px 10px rgba(255, 152, 0, 0.1);
                font-family: 'Nunito', sans-serif;
                min-height: 200px;
                position: relative;
                overflow: hidden;
            }
            .fact-icon {
                font-size: 36px;
                display: block;
                margin-bottom: 10px;
                text-align: center;
            }
            .fact-text {
                font-size: 18px;
                color: #555;
                margin-bottom: 15px;
                line-height: 1.5;
                font-weight: 500;
            }
            .fact-footer {
                font-size: 14px;
                color: #FF9800;
                font-style: italic;
                text-align: right;
                margin-top: 15px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Define the list of facts
            if 'fact_index' not in st.session_state:
                st.session_state.fact_index = 0
                
            facts = [
                {"icon": "🥦", "text": "Broccoli contains more protein than steak per calorie!"},
                {"icon": "🍎", "text": "An apple a day keeps the doctor away because they contain antioxidants that help boost your immune system."},
                {"icon": "🥕", "text": "Carrots can help you see in the dark because they're full of vitamin A, which is good for your eyes."},
                {"icon": "🍓", "text": "Strawberries have more vitamin C than oranges!"},
                {"icon": "🥛", "text": "Drinking milk builds strong bones because it's full of calcium."},
                {"icon": "💪", "text": "Eating protein helps your muscles grow strong and healthy!"},
                {"icon": "🧠", "text": "Healthy foods help your brain think better at school."},
                {"icon": "🏃", "text": "Eating a balanced diet gives you energy to run and play all day long."},
                {"icon": "⭐", "text": "You're doing a great job learning about healthy foods!"},
                {"icon": "🌈", "text": "Try to eat foods of different colors to get all the vitamins your body needs."},
                {"icon": "🎯", "text": "Great choices make a healthy body! You're making awesome decisions!"},
                {"icon": "🎮", "text": "Healthy eating gives you more energy for the things you love to do!"}
            ]
            
            # Display a fact and update index for next time
            current_fact = facts[st.session_state.fact_index]
            st.session_state.fact_index = (st.session_state.fact_index + 1) % len(facts)
            footers = [
                "Eat healthy and stay strong!",
                "Healthy food, happy mood!",
                "Good food gives you superpowers!",
                "Strong bodies start with smart bites!",
                "Snack smart, grow strong!"
            ]
            footer_text = random.choice(footers)
            
            # Display the current fact in the container
            fact_html = f"""
            <div class="fact-container">
                <div class="fact-icon">{current_fact["icon"]}</div>
                <div class="fact-text">{current_fact["text"]}</div>
                <div class="fact-footer">{footer_text}</div>
            </div>
            """
            st.markdown(fact_html, unsafe_allow_html=True)
            



    # Progress bar
    progress = st.session_state.correct_sorts / max(1, st.session_state.items_sorted)
    percent = int(progress * 100)

    st.markdown(f"""
        <style>
        .clean-progress-container {{
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 20px;
            padding: 4px;
            margin: 20px 0;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }}

        .clean-progress-fill {{
            height: 20px;
            width: {percent}%;
            background-color: #3b82f6;
            border-radius: 16px;
            transition: width 0.4s ease-in-out;
        }}

        .progress-label {{
            text-align: center;
            margin-top: 8px;
            font-size: 1.1rem;
            font-weight: 500;
            color: #333;
            font-family: 'Arial', sans-serif;
        }}
        </style>

        <div class="clean-progress-container">
            <div class="clean-progress-fill"></div>
        </div>
        <div class="progress-label">{percent}% complete</div>
    """, unsafe_allow_html=True)

    
    
    # Centered Reset Game button
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("🔄 Reset Game"):
        init_game_state()
        st.session_state.current_item = None
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
