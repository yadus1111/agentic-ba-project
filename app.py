from dotenv import load_dotenv
load_dotenv()
import gradio as gr
from config import MODEL_NAME
import google.generativeai as genai
import re
import subprocess
import os
import time
import random
import copy
import socket
import base64
import markdown

# Set up Gemini model using environment variable
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
2. Process Flow according to business problem (as a Mermaid diagram in a code block)
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
5. Use Case Diagrams and detailed Scenarios for all provided cases
   - For each use case, generate a unique, scenario-specific diagram and description. Each diagram must visualize the specific actors, steps, and interactions for that use case, not a generic flow. Use the business problem and the use case scenario details.
   - IMPORTANT: Use ONLY simple Mermaid syntax for use case diagrams
6. Data Mapping Sheet and Data Requirements Analysis (as a Markdown table)
    - For the Data Mapping Sheet, use the following columns:
        | Data Element | Source System(s) | Data Type | Frequency/Freshness | Purpose for Personalization | Availability (Y/N) | PII/Sensitivity (PII, Sensitive, Public) | Data Owner | Transformation/Processing | Remarks/Privacy Concerns |
    - Format as a Markdown table. Be concise and clear.
7. Functional Scope Summary (In/Out of Scope)
8. Suggested KPIs for success measurement

IMPORTANT:
- Format all sections, headings, and lists using Markdown syntax (## for main sections, ### for sub-sections, * for bullet points, 1. for numbered lists, etc.) for maximum readability.
- Use clear Markdown headers for each section (e.g., ## 01. Stakeholder Map).
- Use bullet points and numbered lists for clarity.
- Optionally, add relevant emojis or icons in section headers for visual clarity (e.g., ## 📊 03. Business Requirement Document (BRD)).
- Make the report visually structured and easy to read.
- Do NOT output any generic template content—make all content specific to the provided business problem and use cases.

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

def sanitize_mermaid_code(code):
    def clean_label(label):
        label = re.sub(r'[()&/,"\']', '', label)
        label = re.sub(r'\s+', ' ', label)
        label = re.sub(r'[^\w\s\-]', '', label)
        return label.strip()
    lines = code.splitlines()
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('flowchart') or line.startswith('graph'):
            clean_lines.append(line)
            continue
        if '-->' in line:
            parts = line.split('-->')
            left = parts[0].strip()
            for right in parts[1:]:
                right = right.strip()
                if right:
                    left_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", left)
                    right_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", right)
                    clean_lines.append(f"{left_clean} --> {right_clean}")
                    left = right
        else:
            line_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", line)
            clean_lines.append(line_clean)
    return '\n'.join(clean_lines)

def validate_mermaid_code(code):
    if not re.search(r'^flowchart TD', code, re.MULTILINE):
        return False
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
    if re.search(r'\[[^\]]*[()&/,"\'\{\}\[\]][^\]]*\]', code):
        return False
    return True

def extract_and_render_mermaid(md_text, output_dir=OUTPUT_DIR, business_problem=None):
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", md_text, re.DOTALL)
    image_paths = []
    error_blocks = []
    fixed_blocks = []
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, code in enumerate(mermaid_blocks, 1):
        code = sanitize_mermaid_code(code)
        section_type = None
        if not validate_mermaid_code(code):
            if section_type == 'process':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
            elif section_type == 'stakeholder':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['stakeholder'])
        
        mmd_path = os.path.join(output_dir, f"diagram_{idx}.mmd")
        png_path = os.path.join(output_dir, f"diagram_{idx}.png")
        
        try:
            with open(mmd_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Try to render PNG using mermaid-cli if available
            try:
                # Try different possible mmdc paths
                mmdc_paths = [
                    "mmdc",  # If installed globally
                    "/usr/local/bin/mmdc",  # Common Linux path
                    "/usr/bin/mmdc",  # Alternative Linux path
                    r"C:\Users\acer\AppData\Roaming\npm\mmdc.cmd"  # Windows path
                ]
                
                rendered = False
                for mmdc_path in mmdc_paths:
                    try:
                        result = subprocess.run([
                            mmdc_path, "-i", mmd_path, "-o", png_path
                        ], check=True, capture_output=True, text=True, timeout=30)
                        if os.path.exists(png_path):
                            image_paths.append(png_path)
                            rendered = True
                            break
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                
                if not rendered:
                    # If mmdc is not available, just keep the Mermaid code
                    # The diagrams will be rendered by the frontend using Mermaid.js
                    error_blocks.append((idx, code, "Mermaid CLI not available - diagrams will be rendered in browser"))
                
            except Exception as e:
                error_blocks.append((idx, code, f"mmdc error: {str(e)}"))
            
            fixed_blocks.append((idx, code))
            
        except Exception as e:
            error_blocks.append((idx, code, f"Could not save file: {str(e)}"))
    
    return image_paths, error_blocks, fixed_blocks

def extract_use_case_details(report_text):
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
            code = response.text.strip().replace('```mermaid','').replace('```','').strip()
            code = sanitize_mermaid_code(code)
            return code
        else:
            return None
    except Exception as e:
        return None

def insert_use_case_diagrams(report_text, business_problem):
    use_cases = extract_use_case_details(report_text)
    if not use_cases:
        return report_text  # fallback: nothing to do
    new_report = report_text
    for uc in use_cases:
        diagram_code = generate_use_case_diagram(business_problem, uc)
        if not diagram_code:
            diagram_code = "Diagram could not be generated for this use case."
        # Always insert the diagram code block so it is picked up by the PNG generation pipeline
        uc_pattern = re.compile(rf"(\*\*Use Case {uc['idx']}:\*\*.*?\*\*Main Flow:\*\*.*?)(\n\n|\Z)", re.DOTALL)
        match = uc_pattern.search(new_report)
        if match:
            insert_pos = match.end(1)
            after_main_flow = new_report[insert_pos:insert_pos+200]
            mermaid_match = re.search(r"```mermaid[\s\S]*?```", after_main_flow)
            if mermaid_match:
                start = insert_pos + mermaid_match.start()
                end = insert_pos + mermaid_match.end()
                new_report = new_report[:start] + f"```mermaid\n{diagram_code}\n```\n" + new_report[end:]
            else:
                new_report = new_report[:insert_pos] + f"\n```mermaid\n{diagram_code}\n```\n" + new_report[insert_pos:]
    return new_report

def generate_report_and_images(business_problem):
    prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            report_text = response.text if response.text else "No content generated."
            report_text = insert_use_case_diagrams(report_text, business_problem)
            image_paths, error_blocks, fixed_blocks = extract_and_render_mermaid(report_text, business_problem=business_problem)
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

def ensure_mermaid_diagrams(html_content):
    # Look for <pre><code class="language-mermaid"> or <code> blocks containing mermaid
    mermaid_pattern = r'<pre><code[^>]*class="[^"]*mermaid[^"]*"[^>]*>(.*?)</code></pre>|<pre><code[^>]*>(.*?)</code></pre>'
    
    def replace_mermaid(match):
        # Extract the mermaid code from the match
        mermaid_code = match.group(1) or match.group(2)
        if not mermaid_code or 'flowchart' not in mermaid_code:
            return match.group(0)  # Return original if not mermaid
        
        # Clean the code
        mermaid_code = mermaid_code.strip()
        
        # Create a unique ID for this diagram
        diagram_id = f"mermaid-diagram-{hash(mermaid_code) % 10000}"
        
        # Return the HTML for the diagram
        return f"""
        <div style="margin: 20px 0; padding: 20px; background: #f8fafc; border-radius: 10px; border: 2px solid #e0e7ff; text-align: center;">
            <div class="mermaid" id="{diagram_id}">
{mermaid_code}
            </div>
        </div>
        """
    
    # Replace all mermaid code blocks
    html_content = re.sub(mermaid_pattern, replace_mermaid, html_content, flags=re.DOTALL)
    
    # Add mermaid script if we found any diagrams
    if 'mermaid' in html_content:
        mermaid_script = """
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true
                }
            });
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(function() {
                    mermaid.init();
                }, 1000);
            });
        </script>
        """
        # Insert the script at the beginning
        html_content = mermaid_script + html_content
    
    return html_content

def render_mermaid_blocks(md_text):
    # Split on mermaid code blocks
    parts = re.split(r'```mermaid\s*\n(.*?)```', md_text, flags=re.DOTALL)
    html_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Non-mermaid: convert to HTML
            html_parts.append(markdown.markdown(part, extensions=['tables', 'fenced_code']))
        else:
            # Mermaid: insert as raw HTML
            html_parts.append(f'<div class="mermaid">{part.strip()}</div>')
    html_report = ''.join(html_parts)
    # Add Mermaid.js script at the top
    html_report = (
        '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
        '<script>mermaid.initialize({startOnLoad:true});</script>'
        + f'<div class="html-report">{html_report}</div>'
    )
    return html_report

def gradio_dashboard():
    with gr.Blocks(css="""
.html-report h1, .html-report h2, .html-report h3 {
    color: #3b82f6;
    background: linear-gradient(90deg, #6366f1 0%, #06b6d4 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}
.html-report h2 {
    font-size: 2em;
}
.html-report h3 {
    font-size: 1.3em;
}
.html-report ul, .html-report ol {
    margin-left: 2em;
    margin-bottom: 1em;
}
.html-report li {
    color: #0ea5e9;
    font-size: 1.1em;
    margin-bottom: 0.3em;
}
.html-report table, .html-report th, .html-report td {
    border: 1.5px solid #a5b4fc !important;
    border-collapse: collapse !important;
    padding: 10px 14px !important;
    font-size: 1.05em !important;
    background: #f9fafb !important;
}
.html-report th {
    background: #e0e7ff !important;
    font-weight: bold !important;
    color: #3730a3 !important;
}
.html-report tr:nth-child(even) {
    background: #f3f4f6 !important;
}
.html-report tr:hover {
    background: #fcd34d !important;
}
""") as demo:
        gr.HTML('<h1>💡 Agentic BA Dashboard</h1>')
        gr.Markdown("Welcome to your AI-powered business analysis system!")
        business_problem = gr.Textbox(
            label="Business Problem / Objective", 
            value="", 
            lines=8, 
            placeholder="Paste your business case or objective here..."
        )
        run_btn = gr.Button("Generate Report")
        status = gr.Textbox(label="Status", value="Ready to generate report...", interactive=False)
        report_output = gr.HTML(label="Generated Report")
        def run_and_status(bp):
            try:
                status_msg = "Generating report... (this may take a moment)"
                report, images = generate_report_and_images(bp)
                html_report = render_mermaid_blocks(report)
                final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
                return html_report, final_status
            except Exception as e:
                return f"Error: {str(e)}", "Generation failed"
        run_btn.click(run_and_status, inputs=[business_problem], outputs=[report_output, status])
    return demo

# Create the Gradio app instance for Hugging Face Spaces
demo = gradio_dashboard()

if __name__ == "__main__":
    demo.launch(server_port=7860, share=True)
