import gradio as gr
from config import MODEL_NAME
import google.generativeai as genai
import re
import subprocess
import os
import time
import random
import copy
from datetime import datetime
import json

# Set up Gemini client using environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(MODEL_NAME)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Default prompt template for the full report
REPORT_PROMPT_TEMPLATE = '''
You are an expert Business Analyst specializing in banking and fintech. Given the following business problem/objective, generate a complete business analysis report in Markdown format. The report must include:

1. Stakeholder Map (as a Mermaid diagram in a code block)
   - Use the business problem and list all unique stakeholders relevant to this scenario. Do not use a generic template.
   - IMPORTANT: Use ONLY simple Mermaid syntax: flowchart TD with basic rectangles and arrows
   - NO special characters, NO advanced formatting, NO styling
   - Example format:
   ```mermaid
   flowchart TD
       A[Stakeholder 1] --> B[Stakeholder 2]
       B --> C[Stakeholder 3]
   ```

2. Process Flow of the new loan uptake journey (as a Mermaid diagram in a code block)
   - Use the business problem and describe the unique steps for this specific journey. Do not use a generic template.
   - IMPORTANT: Use ONLY simple Mermaid syntax: flowchart TD with basic rectangles and arrows
   - NO special characters, NO advanced formatting, NO styling
   - Example format:
   ```mermaid
   flowchart TD
       A[Step 1] --> B[Step 2]
       B --> C[Step 3]
   ```

3. Business Requirement Document (BRD)
4. Functional Requirement Specification (FRS), including Non-Functional Requirements
5. Use Case Diagrams and detailed Scenarios for three specific cases
   - For each use case, generate a unique, scenario-specific diagram and description. Each diagram must visualize the specific actors, steps, and interactions for that use case, not a generic flow. Use the business problem and the use case scenario details.
   - IMPORTANT: Use ONLY simple Mermaid syntax for use case diagrams
6. Data Mapping Sheet and Data Requirements Analysis (as a Markdown table)
    - For the Data Mapping Sheet, use the following columns:
        | Data Element | Source System(s) | Data Type | Frequency/Freshness | Purpose for Personalization | Availability (Y/N) | PII/Sensitivity (PII, Sensitive, Public) | Data Owner | Transformation/Processing | Remarks/Privacy Concerns |
    - Format as a Markdown table. Be concise and clear.
7. Functional Scope Summary (In/Out of Scope)
8. Suggested KPIs for success measurement

IMPORTANT MERMAID RULES:
- Use ONLY: flowchart TD
- Use ONLY: basic rectangles [text] and arrows -->
- NO special characters: (), &, /, commas in node labels
- NO advanced features: styling, subgraphs, classDef, etc.
- Keep node labels simple and short
- Test your syntax for Mermaid version 11.5.0

Format each section with a clear Markdown header (e.g., ## 01. Stakeholder Map) and use code blocks for Mermaid diagrams. Make the report clear, structured, and actionable.

Business Problem:
{business_problem}
'''

# --- AGENT DEFINITIONS (imported from agents.py) ---
class ProjectManagerAgent:
    system_message = (
        "You are a Project Manager. Orchestrate the workflow for business analysis of improving loan product uptake in mobile banking. Assign tasks to specialized agents and ensure all deliverables are produced and compiled."
    )

class BusinessAnalystAgent:
    system_message = (
        "You are a Business Analyst specializing in banking. Gather requirements, write the BRD, FRS (including NFRs), scope, and user journey mapping for the loan personalization project."
    )

class DataAnalystAgent:
    system_message = (
        "You are a Data Analyst. Map data requirements, sources, freshness, and gaps for the loan personalization project. Produce a data mapping sheet."
    )

class ProcessModelerAgent:
    system_message = (
        "You are a Process Modeler. Create process flows and user journey diagrams in Mermaid format for the loan personalization project."
    )

class UseCaseAgent:
    system_message = (
        "You are a Use Case Analyst. Develop use case diagrams and detailed scenarios for the three specified cases."
    )

class KpiAgent:
    system_message = (
        "You are a KPI and Success Metrics Analyst. Suggest KPIs and acceptance criteria for the loan personalization project."
    )

class TechnicalWriterAgent:
    system_message = (
        "You are a Technical Writer. Compile all deliverables into Markdown files and ensure clarity and completeness."
    )

# Agent registry for orchestration
AGENTS = {
    "project_manager": ProjectManagerAgent(),
    "business_analyst": BusinessAnalystAgent(),
    "data_analyst": DataAnalystAgent(),
    "process_modeler": ProcessModelerAgent(),
    "use_case": UseCaseAgent(),
    "kpi": KpiAgent(),
    "technical_writer": TechnicalWriterAgent(),
}

STRICT_MERMAID_TEMPLATES = {
    'stakeholder': '''flowchart TD
    A[Bank Customer] --> B[Mobile App]
    B --> C[Personalization Engine]
    C --> D[Data Sources]
    D --> E[Core Banking System]
    D --> F[Transaction System]
    D --> G[KYC System]
    B --> H[Loan Products]
    H --> I[Home Loan]
    H --> J[Personal Loan]
    H --> K[Auto Loan]
    H --> L[Education Loan]
    B --> M[Bank Staff]
    M --> N[Product Managers]
    M --> O[IT Team]
    M --> P[Compliance Team]
''',
    'process': '''flowchart TD
    A[Customer Login] --> B[View Dashboard]
    B --> C[Check Recommendations]
    C --> D[View Loan Offers]
    D --> E[Select Product]
    E --> F[View Details]
    F --> G[Apply for Loan]
    G --> H[Submit Application]
    H --> I[Receive Decision]
''',
}

# Helper to identify section type from code or context
def get_section_type(code):
    if re.search(r'sponsor|steering|business owners|it leadership', code, re.IGNORECASE):
        return 'stakeholder'
    if re.search(r'customer opens app|login authentication|dashboard', code, re.IGNORECASE):
        return 'process'
    return None

def strict_mermaid_prompt(section_type, business_problem, use_case_details=None, process_steps=None, stakeholders=None):
    if section_type == 'stakeholder':
        stakeholder_text = f"\nStakeholders: {stakeholders}" if stakeholders else ""
        return f"Given the following business problem: {business_problem}{stakeholder_text}\nGenerate a unique Mermaid flowchart for a stakeholder map using only rectangles and arrows. No special characters, no advanced formatting. Do not use a generic template."
    if section_type == 'process':
        steps_text = f"\nProcess Steps: {process_steps}" if process_steps else ""
        return f"Given the following business problem: {business_problem}{steps_text}\nGenerate a unique Mermaid flowchart for a process flow using only rectangles and arrows. No special characters, no advanced formatting. Do not use a generic template."
    if section_type == 'use_case' and use_case_details:
        return f"Given the following business problem: {business_problem}\nAnd this use case: {use_case_details}\nGenerate a unique Mermaid diagram that visualizes the specific actors, steps, and interactions for this use case. Use only rectangles and arrows. No generic diagrams."
    return None

def sanitize_mermaid_code(code):
    # Remove or replace problematic characters in node labels
    def clean_label(label):
        # Remove parentheses, ampersands, slashes, commas, quotes, and extra spaces
        label = re.sub(r'[()&/,"\']', '', label)
        label = re.sub(r'\s+', ' ', label)
        # Remove any remaining special characters that might cause issues
        label = re.sub(r'[^\w\s\-]', '', label)
        return label.strip()
    
    # Clean the code
    lines = code.splitlines()
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle flowchart declaration
        if line.startswith('flowchart') or line.startswith('graph'):
            clean_lines.append(line)
            continue
            
        # Handle node definitions with arrows
        if '-->' in line:
            parts = line.split('-->')
            left = parts[0].strip()
            for right in parts[1:]:
                right = right.strip()
                if right:
                    # Clean node labels in brackets
                    left_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", left)
                    right_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", right)
                    clean_lines.append(f"{left_clean} --> {right_clean}")
                    left = right
        else:
            # Handle standalone node definitions
            line_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", line)
            clean_lines.append(line_clean)
    
    return '\n'.join(clean_lines)

def validate_mermaid_code(code):
    # Only allow flowchart TD, no other graph types
    if not re.search(r'^flowchart TD', code, re.MULTILINE):
        return False
    
    # Check for forbidden features
    forbidden_patterns = [
        r'style\s+',
        r'subgraph\s+',
        r'classDef\s+',
        r'click\s+',
        r'linkStyle\s+',
        r'end\s+',
        r'class\s+',
        r'%%',
        r'-->|',
        r'---|',
        r'==>',
        r'-.->',
        r'==>',
        r':::',
        r'{{',
        r'}}',
        r'\(\(',
        r'\)\)',
        r'\[\(',
        r'\)\]',
        r'\(\[',
        r'\]\)'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, code):
            return False
    
    # Check for problematic characters in node labels
    if re.search(r'\[[^\]]*[()&/,"\'\{\}\[\]][^\]]*\]', code):
        return False
    
    return True

def extract_and_render_mermaid(md_text, output_dir=OUTPUT_DIR, business_problem=None):
    """Extract Mermaid code blocks and render them using Mermaid Live Editor API"""
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", md_text, re.DOTALL)
    image_paths = []
    error_blocks = []
    fixed_blocks = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, code in enumerate(mermaid_blocks, 1):
        code = sanitize_mermaid_code(code)
        section_type = get_section_type(code)
        
        # Validate code, fallback if invalid
        if not validate_mermaid_code(code):
            if section_type == 'process':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
            elif section_type == 'stakeholder':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['stakeholder'])
        
        try:
            # Use Mermaid Live Editor API to render the diagram
            import requests
            import urllib.parse
            
            # Prepare the request to Mermaid Live Editor API
            api_url = "https://mermaid.ink/svg/"
            
            # Encode the Mermaid code for URL
            encoded_code = urllib.parse.quote(code)
            
            # Create the full URL for the SVG
            svg_url = f"{api_url}{encoded_code}"
            
            # Try to fetch the SVG
            try:
                response = requests.get(svg_url, timeout=10)
                if response.status_code == 200:
                    # Create a data URI for the SVG
                    svg_content = response.text
                    import base64
                    svg_encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                    data_uri = f"data:image/svg+xml;base64,{svg_encoded}"
                    
                    image_paths.append(data_uri)
                    fixed_blocks.append((idx, code, data_uri))
                else:
                    # Fallback: use the URL directly
                    image_paths.append(svg_url)
                    fixed_blocks.append((idx, code, svg_url))
                    
            except requests.RequestException:
                # Fallback: save as .mmd file and provide instructions
                mmd_path = os.path.join(output_dir, f"diagram_{idx}.mmd")
                with open(mmd_path, "w", encoding="utf-8") as f:
                    f.write(code)
                image_paths.append(f"diagram_{idx}.mmd")
                fixed_blocks.append((idx, code))
                
        except Exception as e:
            # If everything fails, just continue with the code
            error_blocks.append((idx, code, f"Could not render diagram: {str(e)}"))
    
    return image_paths, error_blocks, fixed_blocks

def extract_use_case_details(report_text):
    """Extract actors and main flow for each use case from the report text."""
    use_cases = []
    pattern = re.compile(r"\*\*Use Case (\d+):\*\*\s*(.*?)\n\*\*Actors:\*\*\s*(.*?)\n(?:\*\*Preconditions:\*\*\s*(.*?)\n)?\*\*Main Flow:\*\*\s*(.*?)(?:\n\*\*|\Z)", re.DOTALL)
    for match in pattern.finditer(report_text):
        idx = int(match.group(1))
        title = match.group(2).strip()
        actors = match.group(3).strip()
        main_flow = match.group(5).strip()
        use_cases.append({
            'idx': idx,
            'title': title,
            'actors': actors,
            'main_flow': main_flow
        })
    return use_cases

def generate_use_case_diagram(business_problem, use_case):
    prompt = f"""
Given the following business problem: {business_problem}
And this use case: {use_case['title']}
Actors: {use_case['actors']}
Main Flow: {use_case['main_flow']}
Generate a unique Mermaid diagram (flowchart TD) that visualizes the specific actors, steps, and interactions for this use case. Use only rectangles and arrows. No generic diagrams. No advanced formatting. Output only the Mermaid code, no extra text.
"""
    try:
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "No content generated."
    except Exception as e:
        return f"Error generating use case diagram: {str(e)}"

def insert_use_case_diagrams(report_text, business_problem):
    use_cases = extract_use_case_details(report_text)
    if not use_cases:
        return report_text  # fallback: nothing to do
    new_report = report_text
    for uc in use_cases:
        diagram_code = generate_use_case_diagram(business_problem, uc)
        if not diagram_code:
            # fallback: use strict prompt with scenario details
            strict_prompt = f"Given the following business problem: {business_problem}\nAnd this use case: {uc['title']}\nActors: {uc['actors']}\nMain Flow: {uc['main_flow']}\nGenerate a simple Mermaid flowchart TD diagram. Use only rectangles and arrows. No advanced formatting."
            try:
                response = model.generate_content(strict_prompt)
                if response.text:
                    return response.text
                else:
                    return "No content generated."
            except Exception as e:
                return f"Error generating use case diagram: {str(e)}"
        # Insert or replace diagram in the report
        uc_pattern = re.compile(rf"(\*\*Use Case {uc['idx']}:\*\*.*?\*\*Main Flow:\*\*.*?)(\n\n|\Z)", re.DOTALL)
        match = uc_pattern.search(new_report)
        if match:
            insert_pos = match.end(1)
            # Remove any existing mermaid code block right after main flow
            after_main_flow = new_report[insert_pos:insert_pos+200]
            mermaid_match = re.search(r"```mermaid[\s\S]*?```", after_main_flow)
            if mermaid_match:
                # Replace existing
                start = insert_pos + mermaid_match.start()
                end = insert_pos + mermaid_match.end()
                new_report = new_report[:start] + f"```mermaid\n{diagram_code}\n```\n" + new_report[end:]
            else:
                # Insert new
                new_report = new_report[:insert_pos] + f"\n```mermaid\n{diagram_code}\n```\n" + new_report[insert_pos:]
    return new_report

def generate_report_and_images(business_problem):
    prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            report_text = response.text if response.text else "No content generated."
            # --- Insert unique use case diagrams ---
            report_text = insert_use_case_diagrams(report_text, business_problem)
            image_paths, error_blocks, fixed_blocks = extract_and_render_mermaid(report_text, business_problem=business_problem)
            
            # Replace Mermaid code blocks with rendered images
            mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
            mermaid_blocks = re.findall(mermaid_pattern, report_text, re.DOTALL)
            
            for i, (code, image_path) in enumerate(zip(mermaid_blocks, image_paths)):
                if image_path.startswith('data:image/svg+xml'):
                    # Replace with embedded SVG image
                    replacement = f'<div style="text-align: center; margin: 20px 0;"><img src="{image_path}" style="max-width: 100%; height: auto;" alt="Diagram {i+1}"></div>'
                    report_text = re.sub(mermaid_pattern, replacement, report_text, count=1)
                elif image_path.startswith('https://'):
                    # Replace with external SVG URL
                    replacement = f'<div style="text-align: center; margin: 20px 0;"><img src="{image_path}" style="max-width: 100%; height: auto;" alt="Diagram {i+1}"></div>'
                    report_text = re.sub(mermaid_pattern, replacement, report_text, count=1)
                else:
                    # Fallback: keep the code block
                    report_text += f"\n\n**✅ Success:** Mermaid diagram {i+1} generated successfully.\n```mermaid\n{code}\n```\n"
            
            if error_blocks:
                for idx, code, err in error_blocks:
                    report_text += f"\n\n**⚠️ Note:** Mermaid diagram {idx} code is available but rendering failed.\n```mermaid\n{code}\n```\n"
            return report_text, image_paths
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "overloaded" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                    print(f"API overloaded, retrying in {wait_time:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"API is currently overloaded. Please try again in a few minutes. Error: {error_msg}", []
            else:
                return f"Error generating report: {error_msg}", []
    return "Failed to generate report after multiple attempts. Please try again later.", []

def ensure_mermaid_diagrams(report):
    """Replace Mermaid code blocks with rendered SVG images"""
    # This function is now handled in generate_report_and_images
    # The diagrams are rendered as SVG images and embedded directly
    return report

def gradio_dashboard():
    with gr.Blocks(css="""
    body {
        background: linear-gradient(120deg, #e0e7ff 0%, #f0fdfa 30%, #f9fafb 60%, #fcd34d 100%, #f472b6 130%);
        background-size: 200% 200%;
        min-height: 100vh;
        animation: gradientBG 12s ease-in-out infinite alternate;
        font-size: 1.25em;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    .gradio-container {
        background: rgba(255,255,255,0.96);
        border-radius: 18px;
        box-shadow: 0 4px 32px rgba(0,0,0,0.10);
        padding: 40px 32px 32px 32px;
        border: 2px solid #06b6d4;
        transition: box-shadow 0.3s, border-color 0.3s;
        border-image: linear-gradient(90deg, #6366f1 0%, #06b6d4 50%, #f472b6 100%) 1;
    }
    .gradio-container:hover {
        box-shadow: 0 8px 40px rgba(99,102,241,0.18);
        border-color: #f472b6;
    }
    .gr-button {
        background: linear-gradient(90deg, #6366f1 0%, #06b6d4 50%, #f472b6 100%);
        color: #fff;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(99,102,241,0.15);
        font-size: 1.2em;
        transition: transform 0.2s, box-shadow 0.2s, background 0.3s;
        border: none;
    }
    .gr-button:hover {
        background: linear-gradient(90deg, #f472b6 0%, #fcd34d 100%);
        transform: scale(1.07);
        box-shadow: 0 4px 16px rgba(6,182,212,0.18);
    }
    .gr-textbox, .gr-markdown {
        background: linear-gradient(90deg, #f0fdfa 0%, #e0e7ff 100%);
        border-radius: 12px;
        border: 1.5px solid #a5b4fc;
        font-size: 1.6em;
        transition: border-color 0.2s, box-shadow 0.2s, background 0.3s;
    }
    .gr-textbox:focus-within {
        border-color: #f472b6;
        box-shadow: 0 0 0 2px #f472b6;
        background: #fff7ed;
    }
    .gr-markdown h1 {
        color: #6366f1;
        font-size: 3.2em;
        margin-bottom: 0.2em;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #6366f1 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .gr-markdown h2 {
        color: #06b6d4;
        font-size: 2.5em;
        background: linear-gradient(90deg, #06b6d4 0%, #fcd34d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .gr-textbox label, .gr-markdown label {
        color: #0ea5e9;
        font-weight: bold;
        font-size: 1.6em;
    }
    .logo {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 18px;
    }
    .logo-emoji {
        font-size: 3.5em;
        margin-right: 12px;
    }
    .logo-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #6366f1;
        letter-spacing: 2px;
    }
    /* Improved Markdown table styling */
    .gr-markdown table, .gr-markdown th, .gr-markdown td {
        border: 1.5px solid #a5b4fc !important;
        border-collapse: collapse !important;
        padding: 10px 14px !important;
        font-size: 1.15em !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
        background: #f9fafb !important;
    }
    .gr-markdown th {
        background: #e0e7ff !important;
        font-weight: bold !important;
        color: #3730a3 !important;
    }
    .gr-markdown tr:nth-child(even) {
        background: #f3f4f6 !important;
    }
    .gr-markdown tr:hover {
        background: #fcd34d !important;
    }
    /* Hide Gradio footer */
    footer, .svelte-1ipelgc, .gradio-container .footer, .gr-footer { display: none !important; }
    /* Mermaid diagram styling */
    .mermaid {
        text-align: center;
        margin: 20px 0;
        padding: 20px;
        background: #f8fafc;
        border-radius: 10px;
        border: 2px solid #e0e7ff;
    }
    /* HTML report styling */
    .html-report {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
    }
    .html-report h1 {
        color: #6366f1;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        border-bottom: 3px solid #e0e7ff;
        padding-bottom: 10px;
    }
    .html-report h2 {
        color: #06b6d4;
        font-size: 2em;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .html-report h3 {
        color: #3730a3;
        font-size: 1.5em;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .html-report p {
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    .html-report table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .html-report th, .html-report td {
        border: 1px solid #e0e7ff;
        padding: 12px 15px;
        text-align: left;
    }
    .html-report th {
        background: #6366f1;
        color: white;
        font-weight: bold;
    }
    .html-report tr:nth-child(even) {
        background: #f8fafc;
    }
    .html-report tr:hover {
        background: #f0f9ff;
    }
    """) as demo:
        
        with gr.Row():
            gr.HTML('<div class="logo"><span class="logo-emoji">💡</span><span class="logo-title">Agentic BA Dashboard</span></div>')
        gr.Markdown("""
Welcome to your AI-powered business analysis system! Generate comprehensive business analysis deliverables with a single click.

**🎯 Diagrams will render automatically in the report!**
        """)
        gr.Markdown("⚠️ **Note:** If you encounter API overload errors, the system will automatically retry up to 3 times with increasing delays.")
        
        business_problem = gr.Textbox(label="Business Problem / Objective", value="", lines=8, placeholder="Paste your business case or objective here...")
        run_btn = gr.Button("Generate Report")
        status = gr.Textbox(label="Status", value="Ready to generate report...", interactive=False)
        report_output = gr.HTML(label="Generated Report")

        def generate_report(bp):
            if not bp.strip():
                return "Please enter a business problem first.", "Ready to generate report..."
            status_msg = "Generating report... (this may take a moment)"
            report, _ = generate_report_and_images(bp)
            
            # Convert markdown to HTML for better rendering
            import markdown
            html_report = markdown.markdown(report, extensions=['tables', 'fenced_code'])
            html_report = f'<div class="html-report">{html_report}</div>'
            
            final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
            return html_report, final_status

        run_btn.click(generate_report, inputs=[business_problem], outputs=[report_output, status])
        
    return demo

if __name__ == "__main__":
    gradio_dashboard().launch(share=True, server_name="0.0.0.0", server_port=7881) 