[** Try the Live App on Streamlit Cloud**](https://agentic-ba-dashboard.streamlit.app/)

# Agentic Business Analysis Dashboard

Welcome to the **Agentic Business Analysis Dashboard**—a project built by me, **Yadu Sharma**, to showcase the power of multi-agent AI for business analysis, with a modern Streamlit interface and advanced diagramming features.

---

##  What is This Project?

This dashboard is an **AI-powered tool** that generates comprehensive business analysis reports and interactive HTML mockups from a simple business problem description. It leverages Google Gemini (via API) and a team of specialized AI agents to produce:
- Stakeholder maps
- Process flows
- Business requirements (BRD, FRS, NFRs)
- Use case diagrams
- Data mapping tables
- KPIs and more
- **Interactive HTML Mockups** (NEW!)

---

##  How Does It Work?

### Complete Workflow

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

6. **HTML Mockup Generation (Optional):**  
   - **Trigger:** Click "Generate Mockup" after creating your business analysis report
   - **AI Analysis:** The system analyzes your business problem to determine application type
   - **Schema Creation:** Generates JSON schema for UI components and layout
   - **HTML Generation:** Converts schema into modern, responsive HTML with CSS
   - **Preview & Download:** View the mockup in the app and download as HTML file

---

## 🖥 Technologies & Code Used

- **Frontend:** Streamlit (for a modern, interactive UI)
- **AI Model:** Google Gemini 2.5 Flash (via API)
- **Diagrams:** Mermaid.js (for process and stakeholder diagrams)
- **PDF Export:** Playwright (local only)
- **Multi-Agent System:** Custom Python classes for each analysis role
- **Secrets Management:** Streamlit Cloud Secrets for API keys

**Key files:**
- `app_streamlit.py` — Main Streamlit app, all logic and UI
- `config.py` — Model configuration
- `Mockup_design/enhanced_agent.py` — HTML mockup generation system
- `requirements.txt` — All dependencies

**Sample outputs:**
- `schemas/sample_banking_schema_1.json` — Example UI schema for banking application
- `schemas/sample_banking_schema_2.json` — Another example UI schema
- `html_mockups/sample_banking_mockup_1.html` — Example HTML mockup for banking application
- `html_mockups/sample_banking_mockup_2.html` — Another example HTML mockup
- `output/sample_mermaid_diagram_1.mmd` — Example Mermaid diagram code
- `output/sample_mermaid_diagram_2.mmd` — Another example Mermaid diagram
- `output/sample_diagram_1.png` — Example generated diagram image
- `output/sample_diagram_2.png` — Another example diagram image
- `output/sample_business_report_1.pdf` — Example business analysis report
- `output/sample_business_report_2.pdf` — Another example business report

---

##  Why Do I See Mermaid Code Instead of Diagrams on Streamlit Cloud?

**Streamlit Cloud does not allow running Playwright or Mermaid CLI for security reasons.**  
- This means the app cannot generate diagram images (PNGs) dynamically in the cloud.
- Instead, you’ll see the Mermaid code block.  
  **You can copy this code and paste it into the [Mermaid Live Editor](https://mermaid.live/) to view the diagram.**
- When you run the app locally, you get full diagram images and PDF export.

---

##  How to Set Up

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

##  Features

- Multi-agent AI system for deep, structured analysis
- Visual diagrams (images locally, code on cloud)
- Full business analysis report (BRD, FRS, use cases, data mapping, KPIs)
- **Interactive HTML Mockup Generation** - AI-powered UI design samples
- Modern, user-friendly Streamlit UI
- Secure API key management

---

## 🎨 HTML Mockup Generation Feature

### How It Works

The HTML mockup generation is an advanced feature that creates interactive UI designs based on your business requirements:

1. **Application Type Detection:**
   - The AI analyzes your business problem and automatically detects the application type
   - Supports: Banking, CRM, E-commerce, Healthcare, Education, HR, Inventory, Project Management, and more

2. **UI Schema Generation:**
   - Creates a detailed JSON schema of UI components
   - Includes layout, positioning, content, and styling information
   - Based on the specific business requirements and detected application type

3. **Dynamic HTML Creation:**
   - Converts the JSON schema into modern, responsive HTML
   - Includes CSS styling for professional appearance
   - Creates interactive elements and proper layout structure

4. **Output & Usage:**
   - **Preview:** View the mockup directly in the Streamlit app
   - **Download:** Save as HTML file for further development
   - **Design Sample:** Use as a starting point for actual development

### What You Get

- **Responsive Design:** Works on desktop, tablet, and mobile
- **Modern UI:** Clean, professional interface with proper styling
- **Interactive Elements:** Buttons, forms, navigation, and data displays
- **Business Context:** UI elements relevant to your specific business case
- **Downloadable:** HTML files you can open in any browser

### Important Note

**This is a design sample and prototype only.** The generated HTML mockups are:
- ✅ **Great for:** Design inspiration, stakeholder presentations, requirement visualization
- ✅ **Perfect for:** Understanding UI requirements, getting stakeholder feedback

**Next Steps:** Use these mockups as a foundation for actual development with proper backend integration, database design, and production-ready code.

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

<<<<<<< HEAD
*Built by Yadu Sharma using Agentic AI principles and Streamlit.*
=======

>>>>>>> e1887fbfb3172a6d0d98a26357446a144ad6d608
