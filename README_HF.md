# Agentic Business Analysis Dashboard

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
- **Diagrams**: Mermaid.js CLI
- **Architecture**: Multi-Agent System

## Setup Required

### 1. Add your Gemini API key as a secret in Hugging Face Spaces:
- Go to Settings → Secrets
- Add: `GEMINI_API_KEY` = your_api_key_here

### 2. Dependencies
The application uses both Python and Node.js dependencies:

**Python (requirements.txt):**
- pyautogen
- python-dotenv
- google-generativeai>=0.8.0
- gradio>=5.0.0

**Node.js (package.json):**
- @mermaid-js/mermaid-cli: ^11.5.0

### 3. Mermaid CLI Installation
The Mermaid CLI is automatically installed via npm when the space builds. The application will try multiple paths:
- `mmdc` (global installation)
- `npx mmdc` (using npx)
- `./node_modules/.bin/mmdc` (local installation)

## Troubleshooting

If diagrams are not generating as images:
1. Check that the Mermaid CLI is installed (should be automatic)
2. Verify your Gemini API key is set correctly
3. The application will fallback to showing Mermaid code blocks if image generation fails

---

*Built with ❤️ using Agentic AI principles* 