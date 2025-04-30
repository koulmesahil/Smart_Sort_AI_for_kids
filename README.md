# SmartSort Kids

An educational game for children ages 3-7 to learn about food groups through an engaging sorting game.

## Overview

SmartSort Kids is a Streamlit-based educational web application with two main components:

1. **Child Mode**: An interactive game where children sort food items into appropriate categories with visual and audio feedback.
2. **Parent Dashboard**: Analytics tracking the child's progress, including accuracy, response times, and AI-generated insights.

## Features

### Child Mode
- Colorful, emoji-based interface designed for young children
- Progressive difficulty levels that adapt to the child's performance
- Optional voice commands and text-to-speech feedback
- Animated elements and encouraging feedback

### Parent Dashboard
- Comprehensive learning analytics
- Progress tracking over time
- Category-specific performance analysis
- Confusion matrix to identify learning patterns
- AI-generated insights about the child's learning

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/smartsort-kids.git
cd smartsort-kids
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

## Running the Application

Run the Streamlit app:
```
streamlit run app.py
```

This will start the app and open it in your default web browser. If it doesn't open automatically, visit `http://localhost:8501` in your web browser.

## Usage

### Child Mode
1. Enter the child's name and age
2. Optionally enable voice features
3. Begin sorting food items by clicking or using voice commands
4. Receive immediate feedback on choices

### Parent Mode
1. Access via the parent tab on the welcome screen or the 👨‍👩‍👧 icon
2. Enter the parent password (default: parent123)
3. View analytics and insights about your child's learning progress



