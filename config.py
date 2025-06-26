import os
from dotenv import load_dotenv

load_dotenv()

# Set your Gemini API key here
GEMINI_API_KEY = "AIzaSyAffhT8tHdD2r-DqvaFhUfcg5F8pU0edok"

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Configuration for the LLM
llm_config = {
    "model": "gemini-1.5-flash-latest",  # Or another suitable Gemini model
    "api_key": GEMINI_API_KEY,
} 