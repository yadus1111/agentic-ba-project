import gradio as gr
from config import MODEL_NAME
import google.generativeai as genai
import re
import subprocess
import os
import time
import random
import copy

from dotenv import load_dotenv
load_dotenv()

# Set up Gemini client using environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(MODEL_NAME)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Default prompt template for the full report
REPORT_PROMPT_TEMPLATE = '''
You are an expert Business Analyst. Given the following business problem/objective, generate a complete business analysis report in Markdown format. The report must include:

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

2. Process Flow (as a Mermaid diagram in a code block)
   - Use the business problem and describe the unique steps for this specific business process. Do not use a generic template.
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
        | Data Element | Source System(s) | Data Type | Frequency/Freshness | Purpose | Availability (Y/N) | PII/Sensitivity (PII, Sensitive, Public) | Data Owner | Transformation/Processing | Remarks/Privacy Concerns |
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

CRITICAL FORMATTING REQUIREMENTS:
- Start with a main title: # [Business Problem] Business Analysis Report
- Use clear section headers: ## 01. Stakeholder Map, ## 02. Process Flow, etc.
- Add proper spacing between sections (2-3 line breaks)
- Use bullet points and numbered lists for better readability
- Format tables properly with clear headers
- Use code blocks for Mermaid diagrams: ```mermaid ... ```
- Make the report well-structured and easy to read
- DO NOT include any plain text flowchart or diagram code outside of mermaid code blocks
- DO NOT repeat or duplicate diagram content

Business Problem:
{business_problem}
'''

# --- AGENT DEFINITIONS (imported from agents.py) ---
class ProjectManagerAgent:
    system_message = (
        "You are a Project Manager. Orchestrate the workflow for business analysis projects. Assign tasks to specialized agents and ensure all deliverables are produced and compiled."
    )

class BusinessAnalystAgent:
    system_message = (
        "You are a Business Analyst. Gather requirements, write the BRD, FRS (including NFRs), scope, and user journey mapping for business analysis projects."
    )

class DataAnalystAgent:
    system_message = (
        "You are a Data Analyst. Map data requirements, sources, freshness, and gaps for business analysis projects. Produce a data mapping sheet."
    )

class ProcessModelerAgent:
    system_message = (
        "You are a Process Modeler. Create process flows and user journey diagrams in Mermaid format for business analysis projects."
    )

class UseCaseAgent:
    system_message = (
        "You are a Use Case Analyst. Develop use case diagrams and detailed scenarios for the three specified cases."
    )

class KpiAgent:
    system_message = (
        "You are a KPI and Success Metrics Analyst. Suggest KPIs and acceptance criteria for business analysis projects."
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
    A[Primary User] --> B[System Interface]
    B --> C[Core System]
    C --> D[Data Sources]
    D --> E[External Systems]
    B --> F[Business Users]
    F --> G[Management]
    F --> H[IT Team]
    F --> I[Support Team]
''',
    'process': '''flowchart TD
    A[User Login] --> B[Access System]
    B --> C[View Options]
    C --> D[Select Function]
    D --> E[Process Request]
    E --> F[Submit Data]
    F --> G[Receive Response]
    G --> H[Complete Task]
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
    """
    Extract and validate Mermaid diagrams from markdown text.
    Convert to HTML blocks with Mermaid.js for proper rendering.
    """
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", md_text, re.DOTALL)
    validated_blocks = []
    error_blocks = []
    
    for idx, code in enumerate(mermaid_blocks, 1):
        code = sanitize_mermaid_code(code)
        section_type = get_section_type(code)
        
        # Validate code, fallback if invalid
        if not validate_mermaid_code(code):
            if section_type == 'process':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
            elif section_type == 'stakeholder':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['stakeholder'])
            else:
                # Generic fallback for unknown section types
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
        
        # Store validated code for HTML rendering
        validated_blocks.append((idx, code))
    
    return [], error_blocks, validated_blocks

def create_mermaid_html(mermaid_code, diagram_id="mermaid-diagram"):
    """
    Create HTML block with Mermaid.js for rendering diagrams.
    """
    html = f"""
    <div style="margin: 20px 0; padding: 15px; border: 1px solid #e0e7ff; border-radius: 8px; background: #f8fafc;">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            if (typeof mermaid !== 'undefined') {{
                mermaid.initialize({{ 
                    startOnLoad: true,
                    theme: 'default',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true
                    }}
                }});
            }}
        </script>
        <div class="mermaid" id="{diagram_id}">
{mermaid_code}
        </div>
    </div>
    """
    return html

def convert_mermaid_to_html(md_text):
    """
    Convert Mermaid code blocks in markdown to HTML blocks with Mermaid.js.
    """
    # Find all mermaid code blocks
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", md_text, re.DOTALL)
    
    # Replace each mermaid block with HTML
    for idx, code in enumerate(mermaid_blocks, 1):
        original_code = code.strip()
        code = sanitize_mermaid_code(original_code)
        section_type = get_section_type(code)
        
        # Validate code, fallback if invalid
        if not validate_mermaid_code(code):
            if section_type == 'process':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
            elif section_type == 'stakeholder':
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['stakeholder'])
            else:
                code = sanitize_mermaid_code(STRICT_MERMAID_TEMPLATES['process'])
        
        # Create HTML for this diagram
        html_block = create_mermaid_html(code, f"diagram-{idx}")
        
        # Replace the mermaid code block with HTML
        original_block = f"```mermaid\n{original_code}\n```"
        md_text = md_text.replace(original_block, html_block, 1)
    
    # Also remove any plain text flowchart that might have been added as fallback
    md_text = re.sub(r'\nflowchart TD\n.*?\n\n', '\n\n', md_text, flags=re.DOTALL)
    
    return md_text

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
    if not model:
        return None
    
    prompt = f"""
Given the following business problem: {business_problem}
And this use case: {use_case['title']}
Actors: {use_case['actors']}
Main Flow: {use_case['main_flow']}
Generate a unique Mermaid diagram (flowchart TD) that visualizes the specific actors, steps, and interactions for this use case. Use only rectangles and arrows. No generic diagrams. No advanced formatting. Output only the Mermaid code, no extra text.
"""
    try:
        response = model.generate_content(
            contents=prompt
        )
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
            # fallback: use strict prompt with scenario details
            strict_prompt = f"Given the following business problem: {business_problem}\nAnd this use case: {uc['title']}\nActors: {uc['actors']}\nMain Flow: {uc['main_flow']}\nGenerate a simple Mermaid flowchart TD diagram. Use only rectangles and arrows. No advanced formatting."
            if model:
                try:
                    response = model.generate_content(
                        contents=strict_prompt
                    )
                    if response.text:
                        diagram_code = response.text.strip().replace('```mermaid','').replace('```','').strip()
                        diagram_code = sanitize_mermaid_code(diagram_code)
                    else:
                        diagram_code = sanitize_mermaid_code(f"flowchart TD\n    A[Actor] --> B[System]")  # last-resort fallback
                except Exception:
                    diagram_code = sanitize_mermaid_code(f"flowchart TD\n    A[Actor] --> B[System]")  # last-resort fallback
            else:
                diagram_code = sanitize_mermaid_code(f"flowchart TD\n    A[Actor] --> B[System]")  # last-resort fallback
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
            response = model.generate_content(
                contents=prompt
            )
            report_text = response.text if response.text else "No content generated."
            
            # Improve markdown formatting first
            report_text = improve_markdown_formatting(report_text)
            
            # --- Insert unique use case diagrams ---
            report_text = insert_use_case_diagrams(report_text, business_problem)
            
            # Convert Mermaid code blocks to HTML with Mermaid.js
            report_text = convert_mermaid_to_html(report_text)
            
            # Validate diagrams (for debugging purposes)
            image_paths, error_blocks, validated_blocks = extract_and_render_mermaid(report_text, business_problem=business_problem)
            
            # Add any validation notes
            if error_blocks:
                for idx, code, err in error_blocks:
                    report_text += f"\n\n**Warning:** Mermaid diagram {idx} had validation issues.\nError: {err}\n"
            
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
    # Only insert diagrams after section headers that match keywords
    keywords = [
        (r"stakeholder.*map", '''```mermaid\nflowchart TD\n    A[Project Sponsor] --> B[Steering Committee]\n    B --> C[Business Owners]\n    B --> D[IT Leadership]\n    C --> E[Product Management]\n    C --> F[Business Users]\n    D --> G[Development Team]\n    D --> H[Data Team]\n    D --> I[Security Team]\n    E --> J[Operations Team]\n    F --> K[End Users]\n    L[External Stakeholders] --> M[Regulatory Bodies]\n```'''),
        (r"process.*flow|flow\s*chart|workflow", '''```mermaid\nflowchart TD\n    A[User Access] --> B[Authentication]\n    B --> C[View Interface]\n    C --> D[Select Function]\n    D --> E[Process Request]\n    E --> F[Submit Data]\n    F --> G[Receive Response]\n    G --> H[Complete Action]\n    H --> I[Service Delivered]\n```'''),
        (r"use case.*diagram|use case.*chart|use case.*graph|use case", '''```mermaid\nflowchart TD\n    Actor1[User] -->|Interacts with| System[Business System]\n    System -->|Provides| Service[Business Service]\n```'''),
        (r"data.*mapping|data.*diagram|data.*chart|data.*flow", '''```mermaid\nflowchart TD\n    DataSource[Business Data] --> Engine[Processing Engine]\n    Engine --> Output[Business Output]\n    Output --> Interface[User Interface]\n```'''),
    ]
    for pattern, template in keywords:
        # Only match section headers (lines starting with # or ##)
        matches = list(re.finditer(rf"^#+\s*(.*{pattern}.*)$", report, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            section_start = match.end()
            next_300 = report[section_start:section_start+300]
            # Check for both mermaid code blocks and HTML divs
            if '```mermaid' not in next_300 and '<div class="mermaid">' not in next_300:
                insert_pos = section_start
                report = report[:insert_pos] + '\n' + template + '\n' + report[insert_pos:]
    return report

def improve_markdown_formatting(report_text):
    """
    Improve the formatting of the markdown report for better readability.
    """
    # Fix main title formatting
    report_text = re.sub(r'^# (.*?) ##', r'# \1\n\n##', report_text, flags=re.MULTILINE)
    
    # Add proper spacing after headers
    report_text = re.sub(r'(#+ .*?)\n', r'\1\n\n', report_text)
    
    # Fix section headers that are running together
    report_text = re.sub(r'## (.*?) ###', r'## \1\n\n###', report_text)
    report_text = re.sub(r'### (.*?) \*\*', r'### \1\n\n**', report_text)
    
    # Add spacing around lists
    report_text = re.sub(r'(\n\* .*?)(\n\* )', r'\1\n\2', report_text)
    report_text = re.sub(r'(\n\d+\. .*?)(\n\d+\. )', r'\1\n\2', report_text)
    
    # Add spacing around tables
    report_text = re.sub(r'(\n\|.*\|)(\n\|)', r'\1\n\2', report_text)
    
    # Add spacing around code blocks
    report_text = re.sub(r'(\n```.*?\n.*?\n```)(\n)', r'\1\n\n\2', report_text)
    
    # Ensure proper spacing between sections
    report_text = re.sub(r'(\n## .*?)(\n## )', r'\1\n\n\2', report_text)
    
    # Remove duplicate/fallback diagrams that appear as plain text
    report_text = re.sub(r'\nflowchart TD\n.*?\n\n', '\n\n', report_text, flags=re.DOTALL)
    
    # Clean up any remaining formatting issues
    report_text = re.sub(r'\n{3,}', '\n\n', report_text)
    
    return report_text

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
    .gr-textbox, .gr-html {
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
    .gr-html h1 {
        color: #6366f1;
        font-size: 3.2em;
        margin-bottom: 0.2em;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #6366f1 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .gr-html h2 {
        color: #06b6d4;
        font-size: 2.5em;
        background: linear-gradient(90deg, #06b6d4 0%, #fcd34d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .gr-textbox label, .gr-html label {
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
    /* Improved table styling for HTML output */
    .gr-html table, .gr-html th, .gr-html td {
        border: 1.5px solid #a5b4fc !important;
        border-collapse: collapse !important;
        padding: 10px 14px !important;
        font-size: 1.15em !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
        background: #f9fafb !important;
    }
    .gr-html th {
        background: #e0e7ff !important;
        font-weight: bold !important;
        color: #3730a3 !important;
    }
    .gr-html tr:nth-child(even) {
        background: #f3f4f6 !important;
    }
    .gr-html tr:hover {
        background: #fcd34d !important;
    }
    /* Hide Gradio footer */
    footer, .svelte-1ipelgc, .gradio-container .footer, .gr-footer { display: none !important; }
    """) as demo:
        with gr.Row():
            gr.HTML('<div class="logo"><span class="logo-emoji">💡</span><span class="logo-title">Agentic BA Dashboard</span></div>')
        gr.Markdown("""
Welcome to your AI-powered business analysis system! Generate comprehensive business analysis deliverables with a single click.
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
            report = ensure_mermaid_diagrams(report)
            final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
            return report, final_status

        run_btn.click(generate_report, inputs=[business_problem], outputs=[report_output, status])
    return demo

if __name__ == "__main__":
    gradio_dashboard().launch(share=True, server_name="0.0.0.0", server_port=7881) 