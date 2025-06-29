import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Configuration for the LLM
llm_config = {
    "model": MODEL_NAME,
    "api_key": GEMINI_API_KEY,
} 