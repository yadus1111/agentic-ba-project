#!/usr/bin/env python3
"""
Script to run the BA Agentic AI FastAPI server
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met"""
    print("=== Checking Requirements ===\n")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ GEMINI_API_KEY not set!")
        print("   Please create a .env file with:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ GEMINI_API_KEY is set")
    
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        import google.generativeai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Please install requirements: pip install -r requirements.txt")
        return False

def run_server():
    """Run the FastAPI server"""
    if not check_requirements():
        return
    
    print("\n=== Starting BA Agentic AI Server ===\n")
    
    try:
        # Import and run the server
        from api.main import app
        import uvicorn
        
        port = int(os.environ.get("PORT", 8000))
        print(f"🚀 Starting server on http://localhost:{port}")
        print("📖 API documentation will be available at http://localhost:8000/docs")
        print("🔍 Health check at http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server\n")
        
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("   Make sure you're in the correct directory and all files are present")

if __name__ == "__main__":
    run_server() 