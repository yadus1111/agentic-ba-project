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

An AI-powered dashboard for generating comprehensive business analysis reports using specialized AI agents with server-side Mermaid diagram rendering.

## Features

- 🤖 **Multi-Agent AI System**: 7 specialized AI agents working together
- 📊 **Visual Diagrams**: Server-side Mermaid diagram rendering via Mermaid Live Editor API
- 📋 **Complete Reports**: BRD, FRS, use cases, data mapping, and KPIs
- 🎨 **Modern UI**: Beautiful Gradio interface with animations
- 🔄 **Error Resilience**: Automatic retries and fallback mechanisms

## How to Use

1. Enter your business problem in the text area
2. Click "Generate Report" 
3. Get a comprehensive business analysis with:
   - Stakeholder maps (rendered as SVG images)
   - Process flows (rendered as SVG images)
   - Business requirements
   - Use case diagrams (rendered as SVG images)
   - Data mapping sheets
   - KPIs and metrics

## Technical Stack

- **Frontend**: Gradio
- **AI Model**: Google Gemini 2.5 Flash
- **Diagrams**: Mermaid.js (server-side rendering via Mermaid Live Editor API)
- **Architecture**: Multi-Agent System

## Setup Required

Add your Gemini API key as a secret in Hugging Face Spaces:
- Go to Settings → Secrets
- Add: `GEMINI_API_KEY` = your_api_key_here

## How It Works

The system uses the Mermaid Live Editor API to render Mermaid diagrams as SVG images on the server side, then embeds them directly in the HTML output. This approach works reliably in Hugging Face Spaces without requiring Docker or additional system dependencies.

## Example Diagrams

The system generates various types of diagrams:

1. **Stakeholder Maps**: Shows relationships between project stakeholders
2. **Process Flows**: Illustrates business processes and user journeys
3. **Use Case Diagrams**: Visualizes specific use case scenarios
4. **Data Flow Diagrams**: Shows data movement and transformations

All diagrams use simple Mermaid syntax for maximum compatibility.

---

*Built with ❤️ using Agentic AI principles*
