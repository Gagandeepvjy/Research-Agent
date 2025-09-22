

# Atlas Guide (LangChain Tool Version)

## How It Works

Atlas Guide is an AI-powered research assistant that automates web research and report generation. It uses LangChain's Tavily tool for web search, trafilatura and PyPDF2 for content extraction, and Google Gemini LLM for summarization and key points. The workflow is orchestrated using LangGraph nodes and results are stored in an SQLite database, accessible via a Flask web interface.

### Architecture & Workflow

-- Add your Gemini API Key and Tavily Search API key into .env file

1. **User submits a query** via the web interface.
2. **Search Node**: Tavily tool fetches up to 6 relevant sources for the query.
3. **Extract Node**: For each source, trafilatura (HTML) or PyPDF2 (PDF) extracts readable text. Blocked or empty sources are skipped.
4. **Repeat search/extract** until at least 2 sources with extractable content are found (up to 5 attempts).
5. **Summarize Node**: Google Gemini LLM summarizes each source and extracts key points.
6. **Report is saved** in SQLite and displayed in the web interface.


```
User Query
   ↓
Search Node (Tavily)
   ↓
Extract Node (trafilatura/PyPDF2)
   ↓
Summarize Node (Gemini LLM)
   ↓
Save & Display Report (Flask/SQLite)
```

## How to Run

1. **Install dependencies**:
   
   pip install flask langchain-google-genai langchain-tavily tiktoken trafilatura PyPDF2 requests
   
2. **Set your API keys** in `agent_tool.py`:
   - Tavily API key
   - Google Gemini API key
3. **Start the Flask app**:
   
   python app.py
   
4. **Open your browser** and go to `http://127.0.0.1:5000/`

## Example Usage
Submit a query like `Latest research on AI in education` or `Impact of Mediterranean diet on heart health` in the web interface. The app will find sources, extract content, summarize, and display a structured report.

## Example Output
- **Summary**: Concise overview from top sources.
- **Key Points**: Bullet points extracted by LLM.
- **Links**: List of URLs to sources.



## AI tools used


   -Used copilot,zencoder for debugging and front end code

