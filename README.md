# Mental Health Chat Assistant

A supportive mental health AI chat assistant built with Streamlit, featuring conversation memory, sentiment analysis, and customizable AI personalities.

## Features

- Real-time chat interface with streaming responses
- Conversation memory persistence using SQLite database
- Sentiment analysis for user messages
- Multiple AI personalities (Friendly, Professional, Therapeutic)
- Mental health resource recommendations
- Model selection with Groq API integration (LLaMA3-8B, Mixtral-8x7B, Claude-3-Opus, Gemma-7B)
- Customizable personality prompts
- Clean and responsive user interface

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd streamlit-chat-app
```

2. Create a single virtual environment:
```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Rename `env_sample.txt` to `.env`
   - Edit the `.env` file to include your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```
   - The default API key is already included in the sample file

## Usage

To run the application:
```bash
# Make sure your virtual environment is activated
python -m streamlit run app.py
```

The application will be available at:
- Local URL: http://localhost:8501
- Network URL: http://your-network-ip:8501

## Project Structure

- `app.py`: Main Streamlit application with chat interface
- `database.py`: Database operations for chat history and prompts
- `state_manager.py`: Manages application state and model configurations
- `mental_health.py`: Sentiment analysis and resource recommendations
- `pages/settings.py`: Settings page for model and personality configuration
- `requirements.txt`: Project dependencies
- `chat_history.db`: SQLite database file for storage

## Dependencies

- Python 3.8+
- Streamlit
- Groq API
- LangChain
- Transformers
- PyTorch
- TextBlob
- Peewee (SQLite ORM)
- Other dependencies listed in requirements.txt

## Contributing

Feel free to fork the repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.
#   M e n t a l _ H e a l t h _ C h a t _ A s s i s t a n t  
 