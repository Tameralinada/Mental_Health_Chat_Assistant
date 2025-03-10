# Mental Health Chat Assistant

A supportive AI-powered mental health chat assistant built with Streamlit, featuring conversation memory, sentiment analysis, and customizable AI personalities. This application provides a safe space for users to discuss their mental health concerns and receive supportive responses.

<!-- Add a screenshot of your application here -->

## Key Features

- **Interactive Chat Interface**: Real-time conversation with streaming responses for a natural chat experience
- **Conversation Memory**: Persistent chat history using SQLite database
- **Sentiment Analysis**: Automatic detection of user message sentiment to provide appropriate responses
- **Multiple AI Personalities**:
  - **Friendly**: Casual and supportive conversational style
  - **Professional**: Clinical and structured therapeutic approach
  - **Therapeutic**: Empathetic and focused on emotional well-being
- **Mental Health Resources**: Contextual recommendations based on conversation content
- **Advanced AI Models**: Integration with Groq API for high-quality responses
  - LLaMA3-8B (default)
  - Mixtral-8x7B
  - Claude-3-Opus
  - Gemma-7B
- **Customizable Settings**: Adjust personality prompts and model parameters
- **Responsive UI**: Clean and intuitive user interface designed for accessibility

## Prerequisites

- Python 3.8 or higher
- Groq API key (a default key is provided)
- Internet connection for API access

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Tameralinada/Mental_Health_Chat_Assistant.git
cd Mental_Health_Chat_Assistant
```

2. **Create a virtual environment**:
```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

3. **Install the required dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
   - The application uses a `.env` file for configuration
   - A default Groq API key is already included in the code
   - To use your own API key:
     - Create a `.env` file in the project root
     - Add your Groq API key: `GROQ_API_KEY=your_groq_api_key_here`

## Usage

### Starting the Application

```bash
# Make sure your virtual environment is activated
streamlit run app.py
```

The application will be available at:
- Local URL: http://localhost:8501
- Network URL: http://your-network-ip:8501

### Using the Chat Interface

1. **Start a conversation**: Type your message in the input field and press Enter or click the Send button
2. **Change personality**: Select your preferred AI personality from the sidebar
3. **View chat history**: Your conversation is saved automatically and displayed in the chat area
4. **Access settings**: Navigate to the Settings page to customize the application

### Settings Page

The Settings page allows you to:
- Select different AI models
- Customize personality prompts
- Adjust model parameters (temperature, max tokens)
- View debug information

## Project Structure

```
Mental_Health_Chat_Assistant/
├── app.py                  # Main Streamlit application
├── database.py             # Database operations
├── state_manager.py        # Application state management
├── mental_health.py        # Sentiment analysis and resources
├── pages/                  # Additional Streamlit pages
│   ├── mental_health.py    # Mental health resources page
│   └── settings.py         # Settings and configuration page
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore file
└── README.md               # Project documentation
```

## Technical Details

### Core Components

- **Streamlit**: Web interface and application framework
- **Groq API**: Cloud-based language models for generating responses
- **SQLite**: Local database for storing chat history
- **TextBlob**: Sentiment analysis for user messages
- **LangChain**: Framework for working with language models

### Conversation Context

The application maintains a 5-message conversation context window to provide relevant and contextual responses while balancing API usage.

### Sentiment Analysis

User messages are analyzed for sentiment (positive, negative, neutral) to help the AI provide appropriate responses and resources.

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

---

*Note: This application is designed for educational and supportive purposes only. It is not a substitute for professional mental health care. If you're experiencing a mental health crisis, please contact a mental health professional or crisis hotline immediately.*
