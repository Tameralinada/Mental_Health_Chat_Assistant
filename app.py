"""Main Streamlit chat application."""
import streamlit as st
import logging
import os
import database
import groq
from threading import Thread
from langchain.memory import ConversationBufferWindowMemory
from mental_health import analyze_sentiment, get_resources, format_sentiment_html
from state_manager import StateManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration first
st.set_page_config(page_title="Mental Health AI Assistant", page_icon="", layout="wide")

# Initialize session state using StateManager
StateManager.initialize_state()

# Set API key from session state
if "GROQ_API_KEY" not in st.session_state:
    st.session_state.GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize memory dictionary
if "memories" not in st.session_state:
    st.session_state.memories = {}

def get_or_create_memory(chat_id):
    """Retrieve or create memory for a specific chat session."""
    chat_id = chat_id or "default_chat"
    if chat_id not in st.session_state.memories:
        st.session_state.memories[chat_id] = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key="chat_history")
    return st.session_state.memories[chat_id]

@st.cache_resource(show_spinner=False)
def load_model():
    """Load AI model or use Groq API."""
    model_config = StateManager.get_current_model()
    if model_config.get("api") == "groq":
        st.session_state.model_loaded = True
        return None, None
    return None, None  # Simplified: Actual model loading is handled elsewhere

def generate_response_with_groq(prompt, chat_id=None):
    """Generate a response using Groq API with optimized streaming."""
    try:
        client = groq.Client(api_key=st.session_state.GROQ_API_KEY)
        
        # Get current personality
        personality = StateManager.get_current_personality()
        
        # Get conversation memory
        memory = get_or_create_memory(chat_id)
        
        # Prepare messages for the API
        messages = []
        
        # Add system message with personality
        system_message = f"{personality['prompt']}\n\nYou have access to the conversation history and should use it to maintain context."
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        if memory.chat_memory.messages:
            for msg in memory.chat_memory.messages:
                role = "user" if msg.type == "human" else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        # Add the current user message
        messages.append({"role": "user", "content": prompt})
        
        # Get the model configuration
        model_config = StateManager.get_current_model()
        model_name = model_config.get("name", "llama3-8b-8192")

        # Create API parameters (excluding unsupported parameters)
        api_params = {
            "model": model_name,
            "messages": messages,
            "temperature": st.session_state.model_params["temperature"],
            "max_tokens": st.session_state.model_params["max_length"],
            "stream": True
        }
        
        # Add top_p if it exists
        if "top_p" in st.session_state.model_params:
            api_params["top_p"] = st.session_state.model_params["top_p"]
        
        # Note: repetition_penalty is not directly supported by Groq API
        # We'll handle it in the prompt if needed

        stream = client.chat.completions.create(**api_params)

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        logger.error(f"Error in Groq API call: {str(e)}")
        yield "Sorry, I encountered an error."

def process_message(message, role="user"):
    """Process and store chat messages."""
    try:
        if role == "user":
            sentiment_info = analyze_sentiment(message)
            st.session_state.sentiment_history.append(sentiment_info)
            st.markdown(format_sentiment_html(sentiment_info), unsafe_allow_html=True)
            
            # Show resources if sentiment is negative
            if sentiment_info["mood"] == "negative" and sentiment_info["confidence"] > 0.5:
                st.session_state.show_resources = True

        chat_id = database.save_message(st.session_state.current_chat_id, role, message)
        if chat_id != st.session_state.current_chat_id and chat_id is not None:
            st.session_state.current_chat_id = chat_id
            
        memory = get_or_create_memory(st.session_state.current_chat_id)
        if role == "user":
            memory.chat_memory.add_user_message(message)
        else:
            memory.chat_memory.add_ai_message(message)

        # Update chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append({"role": role, "content": message})

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        st.error("Error processing message.")

# Main Chat UI
st.title("💭 Mental Health Chat Assistant")

# Display chat history
if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("How are you feeling today?"):
    if not st.session_state.current_chat_id:
        chat_id = database.create_chat("New Conversation")
        if chat_id:
            st.session_state.current_chat_id = chat_id

    with st.chat_message("user"):
        st.markdown(prompt)

    process_message(prompt, role="user")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        for response_chunk in generate_response_with_groq(prompt, st.session_state.current_chat_id):
            full_response += response_chunk
            message_placeholder.markdown(full_response + "▌")  # Streaming effect
        
        message_placeholder.markdown(full_response)
        process_message(full_response, role="assistant")

# Show Mental Health Resources
if st.session_state.show_resources:
    with st.expander("Mental Health Resources", expanded=True):
        for resource in get_resources():
            st.markdown(f"### {resource['name']}\n{resource['description']}\n[Visit Website]({resource['url']})")
