#!/usr/bin/env python3
"""
Deployment script for Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git():
    """Check if git is available"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_space_files():
    """Create necessary files for Hugging Face Spaces"""
    files_to_create = {
        "app.py": """from ba_dashboard import gradio_dashboard

# Create the Gradio app
demo = gradio_dashboard()

# Launch the app (this will be used by Hugging Face Spaces)
if __name__ == "__main__":
    demo.launch()
""",
        "README.md": """# Agentic Business Analysis Dashboard

An AI-powered dashboard for generating comprehensive business analysis reports using specialized AI agents.

## Features

- 🤖 **Multi-Agent AI System**: 7 specialized AI agents working together
- 📊 **Visual Diagrams**: Automatic Mermaid diagram generation
- 📋 **Complete Reports**: BRD, FRS, use cases, data mapping, and KPIs
- 🎨 **Modern UI**: Beautiful Gradio interface with animations
- 🔄 **Error Resilience**: Automatic retries and fallback mechanisms

## How to Use

1. Enter your business problem in the text area
2. Click "Generate Report" 
3. Get a comprehensive business analysis with:
   - Stakeholder maps
   - Process flows
   - Business requirements
   - Use case diagrams
   - Data mapping sheets
   - KPIs and metrics

## Technical Stack

- **Frontend**: Gradio
- **AI Model**: Google Gemini 2.5 Flash
- **Diagrams**: Mermaid.js
- **Architecture**: Multi-Agent System

## Setup Required

Add your Gemini API key as a secret in Hugging Face Spaces:
- Go to Settings → Secrets
- Add: `GEMINI_API_KEY` = your_api_key_here

---

*Built with ❤️ using Agentic AI principles*
""",
        ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Gradio
.gradio/

# Output files
output/
*.png
*.mmd

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
"""
    }
    
    for filename, content in files_to_create.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created {filename}")

def main():
    print("🚀 Hugging Face Spaces Deployment Helper")
    print("=" * 50)
    
    # Check if git is available
    if not check_git():
        print("❌ Git is not installed or not in PATH")
        print("Please install Git and try again")
        return
    
    # Create necessary files
    print("\n📁 Creating deployment files...")
    create_space_files()
    
    print("\n📋 Next Steps:")
    print("1. Go to https://huggingface.co/spaces")
    print("2. Click 'Create new Space'")
    print("3. Choose:")
    print("   - Owner: Your username")
    print("   - Space name: agentic-ba-dashboard")
    print("   - Space SDK: Gradio")
    print("   - Space hardware: CPU (free)")
    print("4. Upload these files to your space:")
    print("   - app.py")
    print("   - ba_dashboard.py")
    print("   - config.py")
    print("   - agents.py")
    print("   - requirements.txt")
    print("   - README.md")
    print("   - .gitignore")
    print("5. Add your Gemini API key as a secret:")
    print("   - Go to Settings → Secrets")
    print("   - Add: GEMINI_API_KEY = your_api_key_here")
    print("6. The space will automatically build and deploy!")
    
    print("\n🎉 Your dashboard will be available at:")
    print("https://huggingface.co/spaces/YOUR_USERNAME/agentic-ba-dashboard")

if __name__ == "__main__":
    main() 