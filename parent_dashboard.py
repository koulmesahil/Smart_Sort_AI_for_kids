import streamlit as st
import pandas as pd
import altair as alt
import json
import os
from datetime import datetime, timedelta
import random
import numpy as np

def load_session_data():
    """Load session data from saved files"""
    data = []
    
    # Check if a data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # Try to load JSON files from data directory
    try:
        data_files = [f for f in os.listdir("data") if f.endswith('.json')]
        for file in data_files:
            with open(os.path.join("data", file), 'r') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                else:
                    data.append(file_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.warning(f"Error loading data: {e}")
        
    # If no data, create sample data for demo purposes
    if not data and 'child_name' in st.session_state:
        data = generate_sample_data(st.session_state.child_name, st.session_state.child_age)
        
    return pd.DataFrame(data) if data else pd.DataFrame()

def generate_sample_data(child_name, child_age):
    """Generate sample data for demonstration"""
    from game_data import FOOD_CATEGORIES
    
    data = []
    categories = list(FOOD_CATEGORIES.keys())
    
    # Create 50 sample responses over the past week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    for i in range(50):
        # Random timestamp within the past week
        timestamp = start_date + (end_date - start_date) * random.random()
        
        # Pick a random category and item
        correct_category = random.choice(categories)
        item = random.choice(FOOD_CATEGORIES[correct_category])
        
        # Simulate some errors (wrong category selected)
        is_correct = random.random() > 0.3  # 70% correct rate
        selected_category = correct_category if is_correct else random.choice([c for c in categories if c != correct_category])
        
        # Response time between 1-5 seconds
        response_time = 1 + 4 * random.random()
        
        # Level progression
        level = min(5, max(1, int(i / 10) + 1))
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "item": item,
            "correct_category": correct_category,
            "selected_category": selected_category,
            "is_correct": is_correct,
            "response_time": response_time,
            "level": level,
            "child_name": child_name,
            "child_age": child_age
        })
    
    return data

def generate_ai_insights(df):
    """Generate AI-powered insights from the session data"""
    # In a full implementation, this would call a LLM API
    # Here we'll simulate with conditional logic
    
    insights = []
    
    if df.empty:
        return ["No data available yet. Have your child play the game first!"]
    
    # Calculate key metrics
    total_items = len(df)
    correct_items = df['is_correct'].sum()
    accuracy = correct_items / total_items if total_items > 0 else 0
    avg_response_time = df['response_time'].mean()
    
    # Convert timestamps to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('datetime')
    
    # Get performance over time
    if len(df) >= 10:
        first_half = df.iloc[:len(df)//2]
        second_half = df.iloc[len(df)//2:]
        
        first_accuracy = first_half['is_correct'].mean()
        second_accuracy = second_half['is_correct'].mean()
        
        first_time = first_half['response_time'].mean()
        second_time = second_half['response_time'].mean()
        
        # Improvement insights
        if second_accuracy > first_accuracy:
            improvement = round((second_accuracy - first_accuracy) * 100, 1)
            insights.append(f"🎯 Your child's accuracy improved by {improvement}% over their recent sessions.")
        
        if second_time < first_time:
            time_improvement = round((first_time - second_time) / first_time * 100, 1)
            insights.append(f"⏱️ Response time improved by {time_improvement}% - they're making decisions faster!")
    
    # Category-specific insights
    category_accuracy = df.groupby('correct_category')['is_correct'].mean().reset_index()
    
    if not category_accuracy.empty:
        best_category = category_accuracy.loc[category_accuracy['is_correct'].idxmax()]
        worst_category = category_accuracy.loc[category_accuracy['is_correct'].idxmin()]
        
        insights.append(f"💪 Strength: Your child excels at identifying {best_category['correct_category']} " +
                      f"with {round(best_category['is_correct']*100)}% accuracy.")
        
        if worst_category['is_correct'] < 0.7:
            insights.append(f"🎯 Growth Area: Your child may benefit from more practice with {worst_category['correct_category']} " +
                          f"(current accuracy: {round(worst_category['is_correct']*100)}%).")
    
    # Age-appropriate benchmarks (simulated)
    age_benchmark = {
        "3": {"accuracy": 0.6, "response_time": 4.5},
        "4": {"accuracy": 0.7, "response_time": 4.0},
        "5": {"accuracy": 0.75, "response_time": 3.5},
        "6": {"accuracy": 0.8, "response_time": 3.0},
        "7": {"accuracy": 0.85, "response_time": 2.5}
    }
    
    child_age = df['child_age'].iloc[0] if not df.empty else "5"
    
    if child_age in age_benchmark:
        benchmark = age_benchmark[child_age]
        
        if accuracy > benchmark["accuracy"]:
            insights.append(f"🏆 Your child's accuracy of {round(accuracy*100)}% is above average for {child_age}-year-olds!")
        
        if avg_response_time < benchmark["response_time"]:
            insights.append(f"🚀 Your child's response time is faster than typical {child_age}-year-olds!")
    
    # Random variation to feel more natural
    variation_insights = [
        "📊 Your child seems to learn best with visual examples.",
        "🧩 Try asking your child to explain why they sorted items the way they did.",
        "🍎 Consider doing a sorting activity with real foods at home to reinforce learning.",
        "📱 Short, frequent game sessions may be more effective than longer, less frequent ones.",
        "🧠 Your child's pattern recognition skills are developing nicely through this activity."
    ]
    
    # Add 1-2 random variations
    insights.extend(random.sample(variation_insights, min(2, len(variation_insights))))
    
    return insights

def generate_unique_fact(df):
    """Placeholder for future LLM call to generate a unique fact based on the results"""
    # In the future, this would call an LLM API
    # For now, simulate with some templated facts
    if df.empty:
        return "No data available yet for generating unique insights."
    
    facts = [
        "Did you know that cognitive sorting skills like those practiced in this game are linked to mathematical reasoning abilities?",
        "Children who excel at categorization tasks often show strong vocabulary development as well!",
        "The ability to quickly switch between different sorting rules (cognitive flexibility) is a key executive function skill.",
        "Research suggests that children's categorization abilities develop significantly between ages 3-7.",
        "Providing verbal explanations for sort choices can enhance a child's metacognitive awareness."
    ]
    
    return random.choice(facts) + " (In the future, this will use an LLM to generate unique facts based on your child's specific data.)"

def show_parent_dashboard():
    """Display the parent analytics dashboard"""
    st.markdown("<h1 class='dashboard-title'>Parent Dashboard</h1>", unsafe_allow_html=True)
    
    # Load data
    df = load_session_data()
    
    if df.empty:
        st.warning("No session data available yet. Have your child play the game first!")
        return
    
    # Convert timestamps to datetime for analysis
    df['datetime'] = pd.to_datetime(df['timestamp'])
    
    # Create tabs for different views
    tabs = st.tabs(["Overview", "Response Time Analysis", "Category Analysis", "AI Insights"])
    
    # Tab 1: Overview
    with tabs[0]:
        st.markdown("<h2>Learning Progress Overview</h2>", unsafe_allow_html=True)
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Items Sorted", len(df))
        
        with col2:
            accuracy = df['is_correct'].mean() * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")
        
        with col3:
            avg_time = df['response_time'].mean()
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        
        with col4:
            max_level = df['level'].max()
            st.metric("Current Level", max_level)
        
        # Level-based accuracy chart
        st.markdown("<h3>Accuracy by Level</h3>", unsafe_allow_html=True)
        
        # Group by level and calculate accuracy
        level_stats = df.groupby('level').agg({
            'is_correct': 'mean',
            'response_time': 'mean',
            'item': 'count'
        }).reset_index()
        
        level_stats['accuracy'] = level_stats['is_correct'] * 100
        
        # Line chart showing accuracy by level
        level_chart = alt.Chart(level_stats).mark_line(point=True).encode(
            x=alt.X('level:O', title='Level'),
            y=alt.Y('accuracy:Q', title='Accuracy (%)', scale=alt.Scale(domain=[0, 100])),
            tooltip=['level', alt.Tooltip('accuracy:Q', format='.1f'), 
                    alt.Tooltip('item:Q', title='Items'), 
                    alt.Tooltip('response_time:Q', format='.2f', title='Avg Response Time')]
        ).properties(
            title='Accuracy Progression by Level',
            height=250
        )
        
        st.altair_chart(level_chart, use_container_width=True)
        
        # Text explanation for level accuracy chart
        level_progress = level_stats['accuracy'].pct_change().fillna(0) * 100
        avg_level_progress = level_progress[1:].mean()  # Skip first level since it has no previous level
        
        highest_level = level_stats.loc[level_stats['level'].idxmax()]
        
        level_explanation = f"""
        **Level-Based Accuracy Analysis:**
        
        - Your child's current highest level is **Level {int(highest_level['level'])}** with an accuracy of **{highest_level['accuracy']:.1f}%**.
        - The average response time at this level is **{highest_level['response_time']:.2f} seconds**.
        """
        
        if len(level_stats) >= 2:
            if avg_level_progress > 0:
                level_explanation += f"\n- On average, your child's accuracy **improved by {abs(avg_level_progress):.1f}%** with each level progression."
            elif avg_level_progress < 0:
                level_explanation += f"\n- On average, your child's accuracy **decreased by {abs(avg_level_progress):.1f}%** with each level progression, which is normal as difficulty increases."
            else:
                level_explanation += "\n- Your child's accuracy has remained **consistent** across levels, showing stable performance as difficulty increases."
            
            # Add educational insight
            if avg_level_progress < -10:
                level_explanation += "\n\n**Educational Insight:** The significant drop in accuracy with higher levels suggests your child may benefit from more practice at the current level before advancing further."
            elif avg_level_progress > 10:
                level_explanation += "\n\n**Educational Insight:** The strong improvement across levels suggests your child is quickly mastering the categorization concepts and may be ready for more challenging activities."
        
        st.markdown(level_explanation)
        
        # Second graph: Items completed per level
        item_chart = alt.Chart(level_stats).mark_bar().encode(
            x=alt.X('level:O', title='Level'),
            y=alt.Y('item:Q', title='Number of Items'),
            color=alt.Color('level:O', legend=None),
            tooltip=['level', 'item']
        ).properties(
            title='Items Completed by Level',
            height=250
        )
        
        st.altair_chart(item_chart, use_container_width=True)
        
        # Text explanation for items by level chart
        max_items = level_stats.loc[level_stats['item'].idxmax()] if not level_stats.empty else None
        min_items = level_stats.loc[level_stats['item'].idxmin()] if not level_stats.empty else None
        
        if max_items is not None and min_items is not None:
            item_explanation = f"""
            **Items Completed Analysis:**
            
            - Your child has completed the most items at **Level {int(max_items['level'])}** ({int(max_items['item'])} items).
            - The fewest items were completed at **Level {int(min_items['level'])}** ({int(min_items['item'])} items).
            """
            
            # Add educational insight based on distribution
            if level_stats['level'].max() > 1 and level_stats.loc[level_stats['level'] == level_stats['level'].max(), 'item'].iloc[0] < 10:
                item_explanation += "\n**Educational Insight:** Consider having your child practice more at the highest level to build confidence with more challenging categorizations."
            
            st.markdown(item_explanation)
        
        # Recent sorting history (moved from Tab 2)
        st.markdown("<h3>Recent Sorting History</h3>", unsafe_allow_html=True)
        
        # Format the data for display
        display_df = df.sort_values('datetime', ascending=False).head(20)[
            ['datetime', 'item', 'correct_category', 'selected_category', 'is_correct', 'response_time', 'level']
        ].copy()
        
        # Format columns for better display
        display_df['datetime'] = display_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
        display_df['response_time'] = display_df['response_time'].round(2).astype(str) + ' sec'
        display_df['is_correct'] = display_df['is_correct'].map({True: '✅', False: '❌'})
        display_df.columns = ['Time', 'Item', 'Correct Category', 'Selected Category', 'Result', 'Response Time', 'Level']
        
        st.dataframe(display_df, use_container_width=True)
    
    # Tab 2: Response Time Analysis (replacing Performance Details)
    with tabs[1]:
        st.markdown("<h2>Response Time Analysis</h2>", unsafe_allow_html=True)
        
        # Response time heatmap by level and correctness
        st.markdown("<h3>Response Time by Level and Outcome</h3>", unsafe_allow_html=True)
        
        # Prepare data for heatmap
        df['response_bin'] = pd.cut(df['response_time'], bins=[0, 1, 2, 3, 4, 5, 10], 
                                    labels=['0-1s', '1-2s', '2-3s', '3-4s', '4-5s', '5+s'])
        
        heatmap_data = df.groupby(['level', 'response_bin', 'is_correct']).size().reset_index(name='count')
        
        # Create the heatmap
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('response_bin:O', title='Response Time'),
            y=alt.Y('level:O', title='Level'),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='blueorange'), legend=alt.Legend(title='Count')),
            tooltip=['level', 'response_bin', 'is_correct', 'count']
        ).properties(
            height=300
        ).facet(
            column=alt.Column('is_correct:N', title='Outcome', sort=[True, False],
                             header=alt.Header(labelExpr="datum.value ? 'Correct ✅' : 'Incorrect ❌'"))
        ).properties(
            title='Distribution of Response Times by Level and Outcome'
        )
        
        st.altair_chart(heatmap, use_container_width=True)
        
        # Text explanation for the heatmap
        st.markdown("""
        **Response Time Distribution Analysis:**
        
        This heatmap shows how response times are distributed across different levels and whether the responses were correct or incorrect.
        
        - **Darker blue cells** indicate more responses in that combination of level and response time.
        - The left panel shows **correct responses**, while the right panel shows **incorrect responses**.
        - You can see if your child is taking longer to respond at higher levels, or if quick responses tend to be more accurate.
        
        **Educational Insight:** If incorrect responses tend to be faster than correct ones, your child might benefit from taking more time to consider their choices before answering.
        """)
        
        # Response time trend over attempts
        st.markdown("<h3>Response Time Trend</h3>", unsafe_allow_html=True)
        
        # Add attempt number column
        df_sorted = df.sort_values('datetime').copy()
        df_sorted['attempt_number'] = range(1, len(df_sorted) + 1)
        
        # Rolling average of response time
        window = min(10, max(3, len(df_sorted) // 5))  # Adaptive window size
        df_sorted['rolling_avg'] = df_sorted['response_time'].rolling(window=window).mean()
        
        # Create the trend chart
        trend_chart = alt.Chart(df_sorted).mark_line(color='blue').encode(
            x=alt.X('attempt_number:Q', title='Attempt Number'),
            y=alt.Y('rolling_avg:Q', title=f'Response Time (Rolling Avg of {window})')
        ).properties(
            height=300
        )
        
        # Add individual points
        points = alt.Chart(df_sorted).mark_circle(size=60).encode(
            x='attempt_number:Q',
            y='response_time:Q',
            color=alt.Color('is_correct:N', scale=alt.Scale(domain=[True, False], range=['#28a745', '#dc3545']),
                           legend=alt.Legend(title='Correct?')),
            tooltip=['attempt_number', 'item', 'correct_category', 
                    alt.Tooltip('response_time:Q', format='.2f')]
        )
        
        st.altair_chart(trend_chart + points, use_container_width=True)
        
        # Text explanation for response time trend
        correct_count = df_sorted['is_correct'].sum()
        correct_pct = correct_count / len(df_sorted) * 100
        
        recent_avg = df_sorted.iloc[-min(10, len(df_sorted)):]['response_time'].mean()
        overall_avg = df_sorted['response_time'].mean()
        
        trend_explanation = f"""
        **Response Time Trend Analysis:**
        
        - The blue line shows the **rolling average** response time over the past {window} attempts.
        - **Green points** represent correct answers ({correct_count} total, {correct_pct:.1f}% of all attempts).
        - **Red points** represent incorrect answers.
        """
        
        if recent_avg < overall_avg * 0.9:
            trend_explanation += f"\n- Your child's **recent response times** ({recent_avg:.2f}s) are **faster than** their overall average ({overall_avg:.2f}s), showing improvement in decision speed."
        elif recent_avg > overall_avg * 1.1:
            trend_explanation += f"\n- Your child's **recent response times** ({recent_avg:.2f}s) are **slower than** their overall average ({overall_avg:.2f}s). This could indicate more careful consideration or increased difficulty."
        else:
            trend_explanation += f"\n- Your child's **recent response times** ({recent_avg:.2f}s) are **consistent** with their overall average ({overall_avg:.2f}s)."
        
        # Add educational insight
        if df_sorted[df_sorted['is_correct']]['response_time'].mean() > df_sorted[~df_sorted['is_correct']]['response_time'].mean():
            trend_explanation += "\n\n**Educational Insight:** Your child tends to take more time on questions they answer correctly, suggesting that encouraging them to slow down might improve accuracy."
        
        st.markdown(trend_explanation)
        
        # Response time distribution by category
        st.markdown("<h3>Response Time by Category</h3>", unsafe_allow_html=True)
        
        category_box = alt.Chart(df).mark_boxplot().encode(
            x=alt.X('correct_category:N', title='Food Category'),
            y=alt.Y('response_time:Q', title='Response Time (seconds)'),
            color=alt.Color('correct_category:N', legend=None)
        ).properties(
            height=300
        )
        
        st.altair_chart(category_box, use_container_width=True)
        
        # Text explanation for response time by category
        category_times = df.groupby('correct_category')['response_time'].agg(['mean', 'median', 'min', 'max']).reset_index()
        fastest_category = category_times.loc[category_times['mean'].idxmin()]
        slowest_category = category_times.loc[category_times['mean'].idxmax()]
        
        time_explanation = f"""
        **Response Time by Category Analysis:**
        
        This boxplot shows the distribution of response times for each food category:
        - The **box** represents the middle 50% of response times
        - The **line in the middle** of each box is the median response time
        - **Dots** represent outliers (unusually fast or slow responses)
        
        **Key Insights:**
        - Your child responds fastest to **{fastest_category['correct_category']}** items (average: {fastest_category['mean']:.2f}s).
        - Your child takes the most time with **{slowest_category['correct_category']}** items (average: {slowest_category['mean']:.2f}s).
        """
        
        # Calculate if there's a correlation between slower categories and accuracy
        category_performance = df.groupby('correct_category').agg({
            'is_correct': 'mean',
            'response_time': 'mean'
        }).reset_index()
        
        # Check correlation
        corr = category_performance['is_correct'].corr(category_performance['response_time'])
        
        if abs(corr) > 0.5:
            if corr > 0:
                time_explanation += "\n\n**Educational Insight:** Categories that take longer to answer tend to have higher accuracy. This suggests your child benefits from taking more time to consider their choices."
            else:
                time_explanation += "\n\n**Educational Insight:** Categories that take longer to answer tend to have lower accuracy. This might indicate confusion with these categories rather than careful consideration."
        
        st.markdown(time_explanation)
    
    # Tab 3: Category Analysis
    with tabs[2]:
        st.markdown("<h2>Category Analysis</h2>", unsafe_allow_html=True)
        
        # Accuracy by category
        st.markdown("<h3>Accuracy by Food Category</h3>", unsafe_allow_html=True)
        
        category_stats = df.groupby('correct_category').agg({
            'is_correct': 'mean',
            'response_time': 'mean',
            'item': 'count'
        }).reset_index()
        
        category_stats['accuracy'] = category_stats['is_correct'] * 100
        
        cat_chart = alt.Chart(category_stats).mark_bar().encode(
            x=alt.X('correct_category:N', title='Food Category', sort='-y'),
            y=alt.Y('accuracy:Q', title='Accuracy (%)'),
            color=alt.Color('correct_category:N', legend=None),
            tooltip=['correct_category', 
                    alt.Tooltip('accuracy:Q', format='.1f'), 
                    alt.Tooltip('item:Q', title='Count'),
                    alt.Tooltip('response_time:Q', format='.2f', title='Avg Response Time')]
        ).properties(
            height=300
        )
        
        st.altair_chart(cat_chart, use_container_width=True)
        
        # Text explanation for the category accuracy chart
        best_category = category_stats.loc[category_stats['accuracy'].idxmax()]
        worst_category = category_stats.loc[category_stats['accuracy'].idxmin()]
        
        st.markdown(f"""
        **Category Performance Analysis:**
        
        - Your child's highest accuracy is with **{best_category['correct_category']}** at **{best_category['accuracy']:.1f}%** 
          (based on {best_category['item']:.0f} items with average response time of {best_category['response_time']:.2f} seconds).
        
        - The most challenging category is **{worst_category['correct_category']}** with **{worst_category['accuracy']:.1f}%** accuracy 
          (based on {worst_category['item']:.0f} items with average response time of {worst_category['response_time']:.2f} seconds).
        
        - The average accuracy across all categories is **{category_stats['accuracy'].mean():.1f}%**.
        """)
        
        # Confusion matrix
        st.markdown("<h3>Confusion Matrix</h3>", unsafe_allow_html=True)
        st.markdown("Where items were sorted vs. where they should be sorted:", unsafe_allow_html=True)
        
        # Create a pivot table for the confusion matrix
        if len(df) > 0:
            confusion = pd.crosstab(df['correct_category'], df['selected_category'], 
                                   normalize='index').round(2) * 100
            
            # Create a heatmap
            conf_data = confusion.reset_index().melt(id_vars=['correct_category'], 
                                                   var_name='selected_category', 
                                                   value_name='percentage')
            
            heatmap = alt.Chart(conf_data).mark_rect().encode(
                x=alt.X('selected_category:N', title='Selected Category'),
                y=alt.Y('correct_category:N', title='Correct Category'),
                color=alt.Color('percentage:Q', scale=alt.Scale(scheme='blues'), legend=alt.Legend(title='% of Items')),
                tooltip=['correct_category', 'selected_category', alt.Tooltip('percentage:Q', format='.1f')]
            ).properties(
                height=300
            )
            
            # Add text labels
            text = heatmap.mark_text().encode(
                text=alt.Text('percentage:Q', format='.0f'),
                color=alt.condition(
                    alt.datum.percentage > 50,
                    alt.value('white'),
                    alt.value('black')
                )
            )
            
            st.altair_chart(heatmap + text, use_container_width=True)
            
            # Text explanation for confusion matrix
            # Find the most common misclassifications
            misclass_data = conf_data[
                (conf_data['correct_category'] != conf_data['selected_category']) & 
                (conf_data['percentage'] > 10)
            ].sort_values('percentage', ascending=False)
            
            confusion_text = """
            **Confusion Matrix Insight:**
            
            - Numbers on the diagonal (from top-left to bottom-right) show the percentage of items correctly categorized.
            - Off-diagonal cells show where misclassifications occurred.
            """
            
            if not misclass_data.empty:
                confusion_text += "\n\n**Notable Confusion Patterns:**\n\n"
                
                for _, row in misclass_data.head(3).iterrows():
                    confusion_text += f"- **{row['percentage']:.1f}%** of **{row['correct_category']}** items were incorrectly sorted as **{row['selected_category']}**.\n"
                
                # Add an educational suggestion
                confusion_text += "\n**Educational Suggestion:** Consider activities that help your child distinguish between these commonly confused categories."
            else:
                confusion_text += "\n\n**Great job!** There are no significant confusion patterns - your child is correctly distinguishing between food categories."
            
            st.markdown(confusion_text)
            
        else:
            st.info("Not enough data to generate confusion matrix.")
    
    # Tab 4: AI Insights
    with tabs[3]:
        st.markdown("<h2>AI-Generated Insights</h2>", unsafe_allow_html=True)
        
        insights = generate_ai_insights(df)
        
        for insight in insights:
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
        
        # Note about AI insights
        st.markdown("<p class='insight-note'>These insights are generated based on your child's learning data. " +
                  "For more personalized discussion, consult with an education professional.</p>",
                  unsafe_allow_html=True)
        
        # Add unique fact section (placeholder for future LLM implementation)
        st.markdown("<h3>Did You Know?</h3>", unsafe_allow_html=True)
        unique_fact = generate_unique_fact(df)
        st.markdown(f"<div class='insight-card unique-fact'>{unique_fact}</div>", unsafe_allow_html=True)