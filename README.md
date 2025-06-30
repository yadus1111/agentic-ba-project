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
