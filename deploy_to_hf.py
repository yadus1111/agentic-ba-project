#!/usr/bin/env python3
"""
Deployment script for Hugging Face Spaces
This script helps prepare and deploy the BA Dashboard to Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check if we're in a git repository and if there are uncommitted changes"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️  Warning: You have uncommitted changes.")
            print("   Consider committing them before deployment.")
            return False
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository or git not available")
        return False

def check_hf_hub():
    """Check if huggingface_hub is installed"""
    try:
        import huggingface_hub
        return True
    except ImportError:
        print("❌ Error: huggingface_hub not installed")
        print("   Install it with: pip install huggingface_hub")
        return False

def create_space_config():
    """Create the necessary configuration files for HF Spaces"""
    
    # Create .gitattributes file
    gitattributes_content = """*.py linguist-language=Python
*.md linguist-language=Markdown
*.txt linguist-language=Text
*.html linguist-language=HTML
*.css linguist-language=CSS
*.js linguist-language=JavaScript
"""
    
    with open('.gitattributes', 'w') as f:
        f.write(gitattributes_content)
    
    # Create .gitignore file
    gitignore_content = """# Python
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
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Output files
output/
*.png
*.mmd

# Logs
*.log
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Created .gitattributes and .gitignore files")

def check_files():
    """Check if all necessary files exist"""
    required_files = [
        'app.py',
        'ba_dashboard.py',
        'config.py',
        'requirements.txt',
        'README_HF.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True

def main():
    """Main deployment function"""
    print("🚀 BA Dashboard - Hugging Face Spaces Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_git_status():
        print("\n💡 To fix git issues:")
        print("   1. Initialize git: git init")
        print("   2. Add files: git add .")
        print("   3. Commit: git commit -m 'Initial commit'")
        return
    
    if not check_hf_hub():
        print("\n💡 To install huggingface_hub:")
        print("   pip install huggingface_hub")
        return
    
    if not check_files():
        print("\n💡 Make sure all required files are in the current directory")
        return
    
    # Create configuration files
    create_space_config()
    
    print("\n🎉 Your project is ready for Hugging Face Spaces deployment!")
    print("\n📋 Next steps:")
    print("1. Go to https://huggingface.co/spaces")
    print("2. Click 'Create new Space'")
    print("3. Choose 'Gradio' as the SDK")
    print("4. Set your Space name (e.g., 'ba-agentic-dashboard')")
    print("5. Choose 'Public' or 'Private'")
    print("6. Click 'Create Space'")
    print("7. In your Space settings, add environment variable:")
    print("   - Name: GEMINI_API_KEY")
    print("   - Value: Your Google Gemini API key")
    print("8. Push your code to the Space repository")
    print("\n💡 Alternative: Use the Hugging Face CLI")
    print("   huggingface-cli repo create ba-agentic-dashboard --type space --space-sdk gradio")
    
    print("\n🔧 Manual deployment commands:")
    print("git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME")
    print("git push -u origin main")

if __name__ == "__main__":
    main() 