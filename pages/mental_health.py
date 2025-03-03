import streamlit as st
import sys
import os

# Add parent directory to path to import mental_health module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mental_health import analyze_sentiment, get_resources, format_sentiment_html

st.set_page_config(
    page_title="Mental Health Analytics",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Mental Health Analytics")

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Mood Analysis Dashboard")
    
    # Mood History
    if "sentiment_history" in st.session_state and st.session_state.sentiment_history:
        # Current Mood Section
        current_sentiment = st.session_state.sentiment_history[-1]
        st.markdown(
            f"""
            #### Current Emotional State
            **Mood:** {current_sentiment['mood'].title()}
            
            **Analysis:**
            - Positivity: {int((current_sentiment['polarity'] + 1) * 50)}%
            - Emotional Intensity: {int(current_sentiment['subjectivity'] * 100)}%
            - Confidence: {int(current_sentiment['confidence'] * 100)}%
            """
        )
        
        # Mood History Section
        st.markdown("#### 📈 Mood History")
        history_container = st.container()
        with history_container:
            for sentiment in reversed(st.session_state.sentiment_history[-10:]):
                st.markdown(format_sentiment_html(sentiment), unsafe_allow_html=True)
        
        # Mood Statistics
        st.markdown("#### 📉 Mood Statistics")
        if len(st.session_state.sentiment_history) > 1:
            # Calculate averages
            avg_polarity = sum(s['polarity'] for s in st.session_state.sentiment_history) / len(st.session_state.sentiment_history)
            avg_subjectivity = sum(s['subjectivity'] for s in st.session_state.sentiment_history) / len(st.session_state.sentiment_history)
            
            # Count emotions
            mood_counts = {}
            for s in st.session_state.sentiment_history:
                mood = s['mood']
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Display statistics
            st.markdown(f"""
            **Overall Mood Analysis:**
            - Average Positivity: {int((avg_polarity + 1) * 50)}%
            - Average Emotional Intensity: {int(avg_subjectivity * 100)}%
            
            **Most Common Moods:**
            """)
            
            # Show top 3 moods
            for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                percentage = (count / len(st.session_state.sentiment_history)) * 100
                st.markdown(f"- {mood.title()}: {int(percentage)}%")
    else:
        st.info("Start chatting to see your mood analysis!")

with col2:
    st.markdown("### 🎯 Mental Health Resources")
    
    # Resources tabs
    tab_pos, tab_neu, tab_neg = st.tabs(["Positive", "Neutral", "Negative"])
    
    with tab_pos:
        resources = get_resources("positive")
        for resource in resources:
            with st.expander(f"{resource['title']} 📚"):
                st.write(resource["description"])
                st.markdown(f"[Learn More]({resource['url']})")
    
    with tab_neu:
        resources = get_resources("neutral")
        for resource in resources:
            with st.expander(f"{resource['title']} 📖"):
                st.write(resource["description"])
                st.markdown(f"[Learn More]({resource['url']})")
    
    with tab_neg:
        resources = get_resources("negative")
        for resource in resources:
            with st.expander(f"{resource['title']} 💡"):
                st.write(resource["description"])
                st.markdown(f"[Learn More]({resource['url']})")
                if "contact" in resource:
                    st.write(f"Emergency Contact: {resource['contact']}")
    
    # Quick mood check
    st.markdown("### 🔍 Quick Mood Check")
    mood_text = st.text_area("How are you feeling right now?", height=100)
    if st.button("Analyze Mood"):
        if mood_text:
            sentiment = analyze_sentiment(mood_text)
            st.markdown(format_sentiment_html(sentiment), unsafe_allow_html=True)
            
            # Show relevant resources
            st.markdown("#### Suggested Resources")
            resources = get_resources(sentiment["mood"])
            for resource in resources[:2]:  # Show top 2 resources
                with st.expander(resource["title"]):
                    st.write(resource["description"])
                    st.markdown(f"[Learn More]({resource['url']})")
        else:
            st.warning("Please enter some text to analyze your mood.")
