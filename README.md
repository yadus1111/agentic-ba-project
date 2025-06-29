---
title: Agentic Business Analysis Dashboard
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

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

## Viewing Mermaid Diagrams

The application generates Mermaid code for diagrams. To view them visually:

### Option 1: Use the Mermaid Viewer (Recommended)
1. Open `mermaid_viewer.html` in your web browser
2. Copy the Mermaid code from your generated report
3. Paste it into the text area and click "Render Diagram"
4. View the beautiful visual diagrams!

### Option 2: Online Mermaid Editor
1. Go to [Mermaid Live Editor](https://mermaid.live/)
2. Copy the Mermaid code from your report
3. Paste it into the editor to see the diagram

### Option 3: GitHub/GitLab
- Mermaid diagrams render automatically in GitHub and GitLab markdown files
- Save your report as a `.md` file and view it on these platforms

## Technical Stack

- **Frontend**: Gradio
- **AI Model**: Google Gemini 2.5 Flash
- **Diagrams**: Mermaid.js
- **Architecture**: Multi-Agent System

## Setup Required

Add your Gemini API key as a secret in Hugging Face Spaces:
- Go to Settings → Secrets
- Add: `GEMINI_API_KEY` = your_api_key_here

## Example Diagrams

The system generates various types of diagrams:

1. **Stakeholder Maps**: Shows relationships between project stakeholders
2. **Process Flows**: Illustrates business processes and user journeys
3. **Use Case Diagrams**: Visualizes specific use case scenarios
4. **Data Flow Diagrams**: Shows data movement and transformations

All diagrams use simple Mermaid syntax for maximum compatibility.

---

*Built with ❤️ using Agentic AI principles*
