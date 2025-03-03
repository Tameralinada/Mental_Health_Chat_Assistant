import streamlit as st
import sys
import os
import database

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import from state_manager to get the same models
from state_manager import StateManager

# Initialize session state variables if they don't exist
if "MODELS" not in st.session_state:
    # Use the models from state_manager to ensure consistency
    st.session_state.MODELS = StateManager.get_models()

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Groq-LLaMA3-8B"  # Default to Groq model

if "PERSONALITIES" not in st.session_state:
    st.session_state.PERSONALITIES = StateManager.get_personalities()

if "personality" not in st.session_state:
    st.session_state.personality = "friendly"

if "model_params" not in st.session_state:
    st.session_state.model_params = {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_length": 256,
        "min_length": 1,
        "repetition_penalty": 1.2,
        "presence_penalty": 0.0
    }

if "PROMPTS" not in st.session_state:
    st.session_state.PROMPTS = {}

if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""

# Page config
st.set_page_config(
    page_title="Settings - Mental Health AI Assistant",
    page_icon="⚙️",
    layout="wide"
)

# Title
st.title("⚙️ Settings")

# Create tabs for different settings
tab1, tab2, tab3, tab4 = st.tabs(["Model Settings", "Prompt Templates", "Personality Settings", "Personality Prompts"])

with tab1:
    # Model Selection
    st.header("Model Selection")

    # Model Size Guide
    st.markdown("""
### 💡 Model Size Guide:
- **Small (Fast)**: TinyLlama-Chat, Phi-2
- **Medium (Balanced)**: Groq-LLaMA3-8B, Groq-Gemma-7B
- **Large (Powerful)**: Groq-Mixtral-8x7B, Groq-Claude-3-Opus
""")

    # Choose AI Model
    st.subheader("Choose AI Model")
    model_options = list(st.session_state.MODELS.keys())
    
    # Handle case where selected model is not in the list
    if st.session_state.selected_model not in model_options:
        st.session_state.selected_model = model_options[0]
        
    selected_model = st.selectbox(
        "Select a model",
        model_options,
        index=model_options.index(st.session_state.selected_model),
        format_func=lambda x: f"{x} - {st.session_state.MODELS[x]['description']}"
    )

    # Update selected model
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.session_state.model_loaded = False
        st.success(f"Model changed to {selected_model}! The new model will be loaded when you return to chat.")

    # Model Details
    st.subheader("Model Details")
    selected_model_info = st.session_state.MODELS[selected_model]
    
    # Check if 'api' key exists to distinguish between local and API models
    model_type = "API" if selected_model_info.get('api') else "Local"
    
    st.markdown(f"""
- **Name**: {selected_model_info['name']}
- **Description**: {selected_model_info['description']}
- **Context Length**: {selected_model_info['context_length']} tokens
- **Size Category**: {selected_model_info['size'].title()}
- **Type**: {model_type}
""")

    # Model Parameters
    st.header("Model Parameters")
    with st.form("model_params"):
        col1, col2 = st.columns(2)
        
        with col1:
            temperature = st.slider(
                "Temperature",
                min_value=0.1,
                max_value=2.0,
                value=st.session_state.model_params["temperature"],
                step=0.1,
                help="Higher values make the output more random, lower values make it more focused and deterministic"
            )
            
            top_p = st.slider(
                "Top P",
                min_value=0.1,
                max_value=1.0,
                value=st.session_state.model_params["top_p"],
                step=0.1,
                help="Controls diversity via nucleus sampling"
            )
        
        with col2:
            max_length = st.slider(
                "Max Length",
                min_value=64,
                max_value=4096,
                value=st.session_state.model_params["max_length"],
                step=64,
                help="Maximum number of tokens to generate"
            )
            
            repetition_penalty = st.slider(
                "Repetition Penalty",
                min_value=1.0,
                max_value=2.0,
                value=st.session_state.model_params["repetition_penalty"],
                step=0.1,
                help="Penalizes repetition in generated text"
            )
        
        submit_button = st.form_submit_button("Apply Parameters")
        if submit_button:
            st.session_state.model_params["temperature"] = temperature
            st.session_state.model_params["top_p"] = top_p
            st.session_state.model_params["max_length"] = max_length
            st.session_state.model_params["repetition_penalty"] = repetition_penalty
            st.success("Model parameters updated successfully!")

with tab2:
    st.header("Prompt Templates")
    st.info("This feature will be available in a future update.")

with tab3:
    st.header("Personality Settings")
    
    # Choose Personality
    st.subheader("Choose Personality")
    personality_options = list(st.session_state.PERSONALITIES.keys())
    selected_personality = st.selectbox(
        "Select a personality",
        personality_options,
        index=personality_options.index(st.session_state.personality) if st.session_state.personality in personality_options else 0,
        format_func=lambda x: f"{st.session_state.PERSONALITIES[x]['name']} - {st.session_state.PERSONALITIES[x]['description']}"
    )
    
    # Update selected personality
    if selected_personality != st.session_state.personality:
        st.session_state.personality = selected_personality
        st.success(f"Personality changed to {st.session_state.PERSONALITIES[selected_personality]['name']}!")
    
    # Personality Details
    st.subheader("Personality Details")
    selected_personality_info = st.session_state.PERSONALITIES[selected_personality]
    st.markdown(f"""
- **Name**: {selected_personality_info['name']}
- **Description**: {selected_personality_info['description']}
""")
    
    # Personality Prompt
    st.subheader("System Prompt")
    st.text_area(
        "This is the system prompt used to guide the AI's responses:",
        value=selected_personality_info['prompt'],
        height=200,
        disabled=True
    )

with tab4:
    st.header("Personality Prompts")
    st.write("Edit the prompts for each personality type")

    personalities = StateManager.get_personalities()
    selected_personality_to_edit = st.selectbox(
        "Select Personality to Edit",
        list(personalities.keys()),
        format_func=lambda x: personalities[x]["name"]
    )

    # Get current prompt from database
    prompt_name = f"personality_{selected_personality_to_edit}"
    db_prompt = database.get_prompt(prompt_name)

    if db_prompt:
        current_prompt = db_prompt["content"]
    else:
        current_prompt = personalities[selected_personality_to_edit]["prompt"]

    edited_prompt = st.text_area(
        "Edit Prompt",
        value=current_prompt,
        height=200
    )

    if st.button("Save Personality Prompt"):
        try:
            database.save_prompt(
                prompt_name,
                edited_prompt,
                f"{personalities[selected_personality_to_edit]['name']} personality prompt",
                selected_personality_to_edit == "friendly"  # Set friendly as default
            )
            st.success(f"Saved {personalities[selected_personality_to_edit]['name']} prompt!")
        except Exception as e:
            st.error(f"Error saving prompt: {str(e)}")

# Warning about model loading
st.warning("""
⚠️ Note: Changing models will require reloading when you return to chat. 
Larger models may take longer to load and use more memory.
""")
