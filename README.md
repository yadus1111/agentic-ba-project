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

Welcome to the **Agentic Business Analysis Dashboard**—a project built by me, **Yadu Sharma**, to showcase the power of multi-agent AI for business analysis, with a modern Streamlit interface and advanced diagramming features.

---

## 🌟 What is This Project?

This dashboard is an **AI-powered tool** that generates comprehensive business analysis reports from a simple business problem description. It leverages Google Gemini (via API) and a team of specialized AI agents to produce:
- Stakeholder maps
- Process flows
- Business requirements (BRD, FRS, NFRs)
- Use case diagrams
- Data mapping tables
- KPIs and more

---

## 🚀 How Does It Work?

1. **User Input:**  
   You enter your business problem or objective in the Streamlit app.

2. **AI Orchestration:**  
   The app uses a multi-agent system (implemented in Python) to break down the analysis into specialized tasks (project manager, business analyst, data analyst, process modeler, use case analyst, KPI analyst, technical writer).

3. **Report Generation:**  
   The core function `generate_report_and_images` sends a detailed prompt to Google Gemini, which returns a Markdown report with embedded Mermaid diagram code.

4. **Diagram Handling:**  
   - **Locally:** The app uses Playwright and Mermaid CLI to convert Mermaid code into high-resolution PNG images, which are embedded in the report and PDF.
   - **On Streamlit Cloud:** Due to platform limitations, the app **cannot generate images**. Instead, it displays the Mermaid code blocks directly. You can copy these and view them in the [Mermaid Live Editor](https://mermaid.live/).

5. **PDF Export:**  
   - **Locally:** You can export the full report (with diagrams) as a PDF.
   - **On Streamlit Cloud:** PDF export is disabled due to Playwright/browser limitations.

---

## 🖥️ Technologies & Code Used

- **Frontend:** Streamlit (for a modern, interactive UI)
- **AI Model:** Google Gemini 2.5 Flash (via API)
- **Diagrams:** Mermaid.js (for process and stakeholder diagrams)
- **PDF Export:** Playwright (local only)
- **Multi-Agent System:** Custom Python classes for each analysis role
- **Secrets Management:** Streamlit Cloud Secrets for API keys

**Key files:**
- `app_streamlit.py` — Main Streamlit app, all logic and UI
- `config.py` — Model configuration
- `requirements.txt` — All dependencies

---

## ❓ Why Do I See Mermaid Code Instead of Diagrams on Streamlit Cloud?

**Streamlit Cloud does not allow running Playwright or Mermaid CLI for security reasons.**  
- This means the app cannot generate diagram images (PNGs) dynamically in the cloud.
- Instead, you’ll see the Mermaid code block.  
  **You can copy this code and paste it into the [Mermaid Live Editor](https://mermaid.live/) to view the diagram.**
- When you run the app locally, you get full diagram images and PDF export.

---

## 🔑 How to Set Up

1. **Clone the repo and install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Add your Gemini API key:**
   - For local: add to a `.env` file (not committed to GitHub)
   - For Streamlit Cloud: add in the app’s Secrets as:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     ```
3. **Run locally:**
   ```bash
   streamlit run app_streamlit.py
   ```
4. **Deploy to Streamlit Cloud:**  
   - Push to GitHub, deploy, and add your API key as a secret.

---

## 📸 Demo

**Below are two demo PDFs generated locally (with full diagrams and images):**

- [Demo Case 1: Business Analysis Report (2025-07-14)](output/business_analysis_report_20250714_145942.pdf)
- [Demo Case 2: Business Analysis Report (2025-07-10)](output/business_analysis_report_20250710_175245.pdf)

> _Each PDF demonstrates the full capabilities of the dashboard, including diagrams, tables, and detailed analysis for two different business cases._

---

## 💡 Features

- Multi-agent AI system for deep, structured analysis
- Visual diagrams (images locally, code on cloud)
- Full business analysis report (BRD, FRS, use cases, data mapping, KPIs)
- Modern, user-friendly Streamlit UI
- Secure API key management

---

## 📝 Why I Built This

I created this project to:
- Demonstrate the power of agentic AI for real-world business analysis
- Provide a tool that can generate professional, actionable reports from just a business problem statement
- Explore the integration of advanced diagramming and PDF export in a modern Python web app

---

## ⚠️ Notes

- **Diagram images and PDF export are only available when running locally.**
- **On Streamlit Cloud, you will see Mermaid code blocks instead of images.**
- **Never commit your API key to GitHub—always use secrets!**

---

*Built with ❤️ by Yadu Sharma using Agentic AI principles and Streamlit.*
