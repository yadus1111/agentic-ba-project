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

## Workflow & Code Overview

### How It Works

1. **User Input**:  
   - The user enters a business problem or objective into the Gradio web interface.

2. **AI-Powered Report Generation**:  
   - The core function `generate_report_and_images` takes the business problem and crafts a detailed prompt for Google Gemini (via the Gemini API).
   - The AI generates a comprehensive business analysis report in Markdown, including:
     - Stakeholder maps
     - Process flows
     - BRD, FRS, and NFRs
     - Use case diagrams and scenarios
     - Data mapping tables
     - Functional scope
     - KPIs

3. **Diagram Rendering**:  
   - The report includes Mermaid diagram code blocks.
   - The code extracts these blocks and uses the Mermaid CLI to render them as PNG images, which are then embedded back into the report.

4. **Error Handling & Resilience**:  
   - The system automatically retries up to 3 times if the AI API is overloaded.
   - If a Mermaid diagram fails to render, fallback diagrams or warnings are inserted.

5. **Output**:  
   - The final report (with diagrams) is displayed in the Gradio UI, ready for download or further use.

### Key Code Components

- **`app.py`**:  
  - Main application file containing all functionality
  - `generate_report_and_images(business_problem)`: Main function for generating the report and diagrams.
  - `extract_and_render_mermaid(md_text, ...)`: Finds Mermaid code blocks and renders them as images.
  - `insert_use_case_diagrams(...)`: Ensures each use case scenario has a unique diagram.
  - `gradio_dashboard()`: Launches the Gradio web interface.

- **`config.py`**:  
  - Stores the default Gemini model name.

## Technical Stack

- **Frontend**: Gradio
- **AI Model**: Google Gemini 2.5 Flash
- **Diagrams**: Mermaid.js
- **Architecture**: Multi-Agent System

## Setup Required

Add your Gemini API key as a secret in Hugging Face Spaces:
- Go to Settings → Secrets
- Add: `GEMINI_API_KEY` = your_api_key_here

## Running the Application

```bash
python app.py
```

The application will launch a Gradio web interface that you can access locally or share publicly.

---

*Built with ❤️ using Agentic AI principles*
