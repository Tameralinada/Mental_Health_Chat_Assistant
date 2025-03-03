"""State management for the Streamlit chat application."""
import streamlit as st
from typing import Dict, List, Optional, Any
import database
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the Groq API key from environment variable with fallback
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

class StateManager:
    """Manages application state in a centralized way."""
    
    @staticmethod
    def initialize_state() -> None:
        """Initialize all required session state variables."""
        # Initialize database
        try:
            database.DatabaseManager.initialize_database()
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
            
        defaults = {
            "chat_history": [],
            "current_chat_id": None,
            "model_loaded": False,
            "show_resources": False,
            "sentiment_history": [],
            "current_prompt": "default",  # Default prompt template
            "personality": "friendly",
            "selected_model": "Groq-LLaMA3-8B",  # Default to Groq model
            "model_params": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_length": 256,  # Reduced for faster responses
                "min_length": 10,
                "repetition_penalty": 1.2
            },
            "api_keys": {
                "groq": GROQ_API_KEY  # Set the API key directly
            },
            "use_api": True  # Flag to determine if using API or local model
        }
        
        # Initialize state variables if they don't exist
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Initialize default prompt if not exists
        StateManager.initialize_default_prompt()
        
        # Initialize personality prompts in database
        StateManager.initialize_personality_prompts()
    
    @staticmethod
    def initialize_default_prompt() -> None:
        """Initialize the default prompt template if it doesn't exist."""
        default_prompt = database.get_prompt("default")
        if not default_prompt:
            database.save_prompt(
                "default",
                "You are a helpful AI assistant.",
                "Default system prompt",
                True
            )
    
    @staticmethod
    def initialize_personality_prompts() -> None:
        """Initialize personality prompts in the database."""
        personalities = {
            "friendly": {
                "name": "Friendly",
                "description": "Warm and conversational",
                "prompt": "You are a friendly and helpful mental health AI assistant. Express yourself in a warm and approachable way while maintaining accuracy. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            },
            "professional": {
                "name": "Professional",
                "description": "Direct and clear",
                "prompt": "You are a professional mental health AI assistant. Be direct and clear in your responses. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            },
            "therapeutic": {
                "name": "Therapeutic",
                "description": "Supportive and empathetic",
                "prompt": "You are a therapeutic mental health AI assistant focused on providing emotional support. Respond with empathy and understanding while offering constructive guidance. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            }
        }
        
        # Save each personality prompt to database
        for key, personality in personalities.items():
            prompt_name = f"personality_{key}"
            existing_prompt = database.get_prompt(prompt_name)
            if not existing_prompt:
                database.save_prompt(
                    prompt_name,
                    personality["prompt"],
                    f"{personality['name']} personality prompt",
                    key == "friendly"  # Set friendly as default
                )
    
    @staticmethod
    def get_models() -> Dict[str, Dict[str, Any]]:
        """Get available models configuration."""
        models = {
            "TinyLlama-Chat": {
                "name": "PY007/TinyLlama-1.1B-Chat-v0.3",
                "description": "Fast and efficient chat model",
                "context_length": 512,
                "size": "small",
                "api": False
            },
            "Phi-2": {
                "name": "susnato/phi-2",
                "description": "Good performance and speed",
                "context_length": 512,
                "size": "small",
                "api": False
            }
        }
        
        # Add Groq models if API key is available
        if GROQ_API_KEY:
            models.update({
                "Groq-LLaMA3-8B": {
                    "name": "llama3-8b-8192",
                    "description": "Fast LLaMA3 8B model",
                    "context_length": 8192,
                    "size": "medium",
                    "api": "groq"
                },
                "Groq-Mixtral-8x7B": {
                    "name": "mixtral-8x7b-32768",
                    "description": "Powerful Mixtral 8x7B model",
                    "context_length": 32768,
                    "size": "large",
                    "api": "groq"
                },
                "Groq-Claude-3-Opus": {
                    "name": "claude-3-opus-20240229",
                    "description": "High-quality Claude 3 Opus model",
                    "context_length": 8192,
                    "size": "xlarge",
                    "api": "groq"
                },
                "Groq-Gemma-7B": {
                    "name": "gemma-7b-it",
                    "description": "Google's Gemma 7B model",
                    "context_length": 8192,
                    "size": "medium",
                    "api": "groq"
                }
            })
        
        return models
    
    @staticmethod
    def get_personalities() -> Dict[str, Dict[str, str]]:
        """Get available personality configurations."""
        return {
            "friendly": {
                "name": "Friendly",
                "description": "Warm and conversational",
                "prompt": "You are a friendly and helpful mental health AI assistant. Express yourself in a warm and approachable way while maintaining accuracy. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            },
            "professional": {
                "name": "Professional",
                "description": "Direct and clear",
                "prompt": "You are a professional mental health AI assistant. Be direct and clear in your responses. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            },
            "therapeutic": {
                "name": "Therapeutic",
                "description": "Supportive and empathetic",
                "prompt": "You are a therapeutic mental health AI assistant focused on providing emotional support. Respond with empathy and understanding while offering constructive guidance. IMPORTANT: You have memory of the entire conversation history provided to you. You should acknowledge and remember details shared by the user throughout the conversation. Never claim that you don't remember previous parts of the conversation or that each interaction is new. Maintain context and continuity throughout the conversation."
            }
        }
    
    @staticmethod
    def get_current_model() -> Dict[str, Any]:
        """Get current model configuration."""
        models = StateManager.get_models()
        selected_model = st.session_state.selected_model
        if selected_model not in models:
            # Fallback to first available model
            selected_model = next(iter(models))
            st.session_state.selected_model = selected_model
        return models[selected_model]
    
    @staticmethod
    def get_current_prompt() -> Dict[str, Any]:
        """Get current prompt template."""
        prompt = database.get_prompt(st.session_state.current_prompt)
        if not prompt:
            # Fallback to default prompt
            prompt = database.get_prompt("default")
            st.session_state.current_prompt = "default"
        return prompt
    
    @staticmethod
    def get_current_personality() -> Dict[str, str]:
        """Get the currently selected personality configuration."""
        personalities = StateManager.get_personalities()
        personality = st.session_state.personality
        if personality not in personalities:
            # Fallback to first available personality
            personality = next(iter(personalities))
            st.session_state.personality = personality
        
        # Get personality prompt from database if available
        prompt_name = f"personality_{personality}"
        db_prompt = database.get_prompt(prompt_name)
        
        if db_prompt:
            # Use the prompt from database
            return {
                "name": personalities[personality]["name"],
                "description": personalities[personality]["description"],
                "prompt": db_prompt["content"]
            }
        
        # Fallback to hardcoded prompt
        return personalities[personality]
    
    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        if "api_keys" in st.session_state and provider in st.session_state.api_keys:
            return st.session_state.api_keys[provider]
        return None
    
    @staticmethod
    def update_chat_history(message: Dict[str, str]) -> None:
        """Update chat history with a new message."""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append(message)
    
    @staticmethod
    def clear_chat_history() -> None:
        """Clear current chat history."""
        st.session_state.chat_history = []
        st.session_state.current_chat_id = None
        st.session_state.sentiment_history = []
        st.session_state.show_resources = False
