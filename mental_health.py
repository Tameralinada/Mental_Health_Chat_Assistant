"""Mental health analysis and support module."""
from textblob import TextBlob
import emoji
from typing import Dict, Any, List
import logging
from functools import lru_cache
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Precompile regex patterns for faster text processing
EMOJI_PATTERN = re.compile(r':[a-zA-Z0-9_]+:')
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')

# Simplified resources for faster lookup
MENTAL_HEALTH_RESOURCES = {
    "negative": [
        {
            "title": "Crisis Helpline",
            "description": "24/7 support for emotional crisis",
            "contact": "1-800-273-8255",
            "url": "https://www.crisistextline.org/"
        },
        {
            "title": "Therapy Resources",
            "description": "Find licensed therapists in your area",
            "url": "https://www.psychologytoday.com/us/therapists"
        },
        {
            "title": "Mindfulness Exercises",
            "description": "Simple exercises to help manage stress and anxiety",
            "url": "https://www.mindful.org/meditation/mindfulness-getting-started/"
        }
    ],
    "neutral": [
        {
            "title": "Self-Care Tips",
            "description": "Daily practices for mental wellness",
            "url": "https://www.verywellmind.com/self-care-strategies-overall-stress-reduction-3144729"
        },
        {
            "title": "Mental Health Apps",
            "description": "Recommended apps for mental wellness",
            "url": "https://www.psycom.net/25-best-mental-health-apps"
        }
    ],
    "positive": [
        {
            "title": "Wellness Activities",
            "description": "Activities to maintain positive mental health",
            "url": "https://www.healthline.com/health/mental-health/mental-health-activities"
        },
        {
            "title": "Gratitude Practices",
            "description": "Ways to cultivate gratitude and joy",
            "url": "https://greatergood.berkeley.edu/topic/gratitude"
        }
    ]
}

def clean_text(text: str) -> str:
    """Clean text for faster processing."""
    # Remove emojis using regex (faster than emoji library)
    text = EMOJI_PATTERN.sub('', text)
    # Remove punctuation
    text = PUNCTUATION_PATTERN.sub('', text)
    # Convert to lowercase
    return text.lower().strip()

@lru_cache(maxsize=1000)
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze text sentiment using TextBlob with optimized caching."""
    try:
        # Clean text for faster processing
        text_clean = clean_text(text)
        
        # Quick sentiment check for empty or very short text
        if not text_clean or len(text_clean) < 3:
            return {
                "mood": "neutral",
                "confidence": 0.5,
                "subjectivity": 0.5,
                "polarity": 0.0
            }
        
        # Analyze sentiment
        analysis = TextBlob(text_clean)
        polarity = analysis.sentiment.polarity
        
        # Adjusted thresholds based on TextBlob's typical output range
        # TextBlob polarity ranges from -1 to 1, with 0.5/-0.5 being moderately positive/negative
        if polarity <= -0.3:
            mood = "negative"
        elif polarity >= 0.3:
            mood = "positive"
        else:
            mood = "neutral"
        
        return {
            "mood": mood,
            "confidence": min(abs(polarity * 2), 1.0),  # Scale confidence to be between 0 and 1
            "subjectivity": analysis.sentiment.subjectivity,
            "polarity": polarity
        }
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return {
            "mood": "neutral",
            "confidence": 0.5,
            "subjectivity": 0.5,
            "polarity": 0.0
        }

# Cache color lookups for faster UI rendering
@lru_cache(maxsize=10)
def get_sentiment_color(mood: str) -> str:
    """Get color code for sentiment visualization with caching."""
    colors = {
        "positive": "#28a745",
        "neutral": "#ffc107",
        "negative": "#dc3545"
    }
    return colors.get(mood, "#6c757d")

def format_sentiment_html(sentiment_info: Dict[str, Any]) -> str:
    """Create HTML for sentiment visualization."""
    color = get_sentiment_color(sentiment_info["mood"])
    confidence = int(sentiment_info["confidence"] * 100)
    
    return f"""
    <div style="
        background-color: {color};
        color: white;
        padding: 8px 15px;
        border-radius: 15px;
        display: inline-block;
        font-size: 14px;
        margin: 5px 0;">
        Mood: {sentiment_info["mood"].title()} ({confidence}%)
    </div>
    """

@lru_cache(maxsize=10)
def get_resources(mood: str) -> List[Dict[str, str]]:
    """Get relevant mental health resources with caching."""
    return MENTAL_HEALTH_RESOURCES.get(mood, MENTAL_HEALTH_RESOURCES["neutral"])

def generate_mental_health_prompt(user_input: str, sentiment_info: Dict[str, Any]) -> str:
    """Generate a mental health-focused prompt based on user input and sentiment."""
    mood = sentiment_info["mood"]
    confidence = sentiment_info["confidence"]
    
    if mood == "negative" and confidence > 0.5:
        return f"""I notice you might be feeling down. I'm here to listen and help. 
        Would you like to talk about what's troubling you, or would you prefer some suggestions for feeling better?"""
    
    elif mood == "positive" and confidence > 0.5:
        return f"""I'm glad you're feeling positive! Would you like to explore ways to maintain this positive energy?"""
    
    else:
        return f"""How can I support you today? I'm here to listen and chat about whatever's on your mind."""
