# app.py for Hugging Face Spaces
# NOTE: Set your GEMINI_API_KEY as a secret in the Hugging Face Space settings!
import os
import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai
import re
import time
import random
import copy
import graphviz

# Load environment variables (for local dev; on Spaces, use Secrets)
load_dotenv()

# Model config
MODEL_NAME = "gemini-2.5-flash"

# Set up Gemini client using environment variable
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

REPORT_PROMPT_TEMPLATE = '''
You are an expert Business Analyst specializing in banking and fintech. Given the following business problem/objective, generate a complete business analysis report in Markdown format. The report must include:

1. Stakeholder Map (as a Graphviz DOT diagram in a code block)
   - Use the business problem and list all unique stakeholders relevant to this scenario. Do not use a generic template.
   - IMPORTANT: Use ONLY simple DOT syntax: digraph G {{ ... }} with basic nodes and arrows
   - NO special characters, NO advanced formatting, NO styling
   - Example format:
   ```dot
   digraph G {{
       A [label="Stakeholder 1"]
       B [label="Stakeholder 2"]
       A -> B
   }}
   ```

2. Process Flow according to the business problem (as a Graphviz DOT diagram in a code block)
   - Use the business problem and describe the unique steps for this specific journey. Do not use a generic template.
   - IMPORTANT: Use ONLY simple DOT syntax: digraph G {{ ... }} with basic nodes and arrows
   - NO special characters, NO advanced formatting, NO styling
   - Example format:
   ```dot
   digraph G {{
       A [label="Step 1"]
       B [label="Step 2"]
       A -> B
   }}
   ```

3. Business Requirement Document (BRD)
4. Functional Requirement Specification (FRS), including Non-Functional Requirements
5. Use Case Diagrams and detailed Scenarios for three specific cases
   - For each use case, generate a unique, scenario-specific diagram and description. Each diagram must visualize the specific actors, steps, and interactions for that use case, not a generic flow. Use the business problem and the use case scenario details.
   - IMPORTANT: Use ONLY simple DOT syntax for use case diagrams
6. Data Mapping Sheet and Data Requirements Analysis (as a Markdown table)
    - For the Data Mapping Sheet, use the following columns:
        | Data Element | Source System(s) | Data Type | Frequency/Freshness | Purpose for Personalization | Availability (Y/N) | PII/Sensitivity (PII, Sensitive, Public) | Data Owner | Transformation/Processing | Remarks/Privacy Concerns |
    - Format as a Markdown table. Be concise and clear.
7. Functional Scope Summary (In/Out of Scope)
8. Suggested KPIs for success measurement

IMPORTANT DOT RULES:
- Use ONLY: digraph G {{ ... }}
- Use ONLY: basic nodes and arrows (->)
- NO special characters: (), &, /, commas in node labels
- NO advanced features: styling, subgraphs, classDef, etc.
- Keep node labels simple and short
- Test your syntax for Graphviz

Format each section with a clear Markdown header (e.g., ## 01. Stakeholder Map) and use code blocks for DOT diagrams. Make the report clear, structured, and actionable.

Business Problem:
{business_problem}
'''

# --- AGENT DEFINITIONS ---
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
        "You are a Process Modeler. Create process flows and user journey diagrams in DOT format for the loan personalization project."
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
AGENTS = {
    "project_manager": ProjectManagerAgent(),
    "business_analyst": BusinessAnalystAgent(),
    "data_analyst": DataAnalystAgent(),
    "process_modeler": ProcessModelerAgent(),
    "use_case": UseCaseAgent(),
    "kpi": KpiAgent(),
    "technical_writer": TechnicalWriterAgent(),
}
STRICT_DOT_TEMPLATES = {
    'stakeholder': '''digraph G {{
    A [label="Bank Customer"]
    B [label="Mobile App"]
    C [label="Personalization Engine"]
    D [label="Data Sources"]
    E [label="Core Banking System"]
    F [label="Transaction System"]
    G [label="KYC System"]
    H [label="Loan Products"]
    I [label="Home Loan"]
    J [label="Personal Loan"]
    K [label="Auto Loan"]
    L [label="Education Loan"]
    M [label="Bank Staff"]
    N [label="Product Managers"]
    O [label="IT Team"]
    P [label="Compliance Team"]
    A -> B
    B -> C
    C -> D
    D -> E
    D -> F
    D -> G
    B -> H
    H -> I
    H -> J
    H -> K
    H -> L
    B -> M
    M -> N
    M -> O
    M -> P
}}''',
    'process': '''digraph G {{
    A [label="Customer Login"]
    B [label="View Dashboard"]
    C [label="Check Recommendations"]
    D [label="View Loan Offers"]
    E [label="Select Product"]
    F [label="View Details"]
    G [label="Apply for Loan"]
    H [label="Submit Application"]
    I [label="Receive Decision"]
    A -> B
    B -> C
    C -> D
    D -> E
    E -> F
    F -> G
    G -> H
    H -> I
}}''',
}
def get_section_type(code):
    if re.search(r'sponsor|steering|business owners|it leadership', code, re.IGNORECASE):
        return 'stakeholder'
    if re.search(r'customer opens app|login authentication|dashboard', code, re.IGNORECASE):
        return 'process'
    return None
def strict_dot_prompt(section_type, business_problem, use_case_details=None, process_steps=None, stakeholders=None):
    if section_type == 'stakeholder':
        stakeholder_text = f"\nStakeholders: {stakeholders}" if stakeholders else ""
        return f"Given the following business problem: {business_problem}{stakeholder_text}\nGenerate a unique DOT diagram for a stakeholder map using only nodes and arrows. No special characters, no advanced formatting. Do not use a generic template."
    if section_type == 'process':
        steps_text = f"\nProcess Steps: {process_steps}" if process_steps else ""
        return f"Given the following business problem: {business_problem}{steps_text}\nGenerate a unique DOT diagram for a process flow using only nodes and arrows. No special characters, no advanced formatting. Do not use a generic template."
    if section_type == 'use_case' and use_case_details:
        return f"Given the following business problem: {business_problem}\nAnd this use case: {use_case_details}\nGenerate a unique DOT diagram that visualizes the specific actors, steps, and interactions for this use case. Use only nodes and arrows. No generic diagrams."
    return None
def sanitize_dot_code(code):
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
        # Fix label attributes missing '=' and quotes
        line = re.sub(r'\[label([^\]=]+)\]', r'[label="\1"]', line)
        if line.startswith('digraph G'):
            clean_lines.append(line)
            continue
        if '->' in line:
            parts = line.split('->')
            left = parts[0].strip()
            for right in parts[1:]:
                right = right.strip()
                if right:
                    left_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", left)
                    right_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", right)
                    clean_lines.append(f"{left_clean} -> {right_clean}")
                    left = right
        else:
            line_clean = re.sub(r'\[(.*?)\]', lambda m: f"[{clean_label(m.group(1))}]", line)
            clean_lines.append(line_clean)
    return '\n'.join(clean_lines)
def validate_dot_code(code):
    if not re.search(r'^digraph G', code, re.MULTILINE):
        return False
    # Add more forbidden patterns if needed
    return True
def extract_and_render_dot(md_text, output_dir="output", business_problem=None):
    dot_blocks = re.findall(r"```dot\n(.*?)```", md_text, re.DOTALL)
    image_paths = []
    error_blocks = []
    fixed_blocks = []
    for idx, code in enumerate(dot_blocks, 1):
        code = sanitize_dot_code(code)
        section_type = None  # Optionally, add logic to detect section type
        # Validate code (basic check)
        if not validate_dot_code(code):
            # fallback to strict template
            if section_type == 'process':
                code = STRICT_DOT_TEMPLATES['process']
            elif section_type == 'stakeholder':
                code = STRICT_DOT_TEMPLATES['stakeholder']
        dot_path = os.path.join(output_dir, f"diagram_{idx}.dot")
        png_path = os.path.join(output_dir, f"diagram_{idx}.png")
        with open(dot_path, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            graph = graphviz.Source(code)
            graph.format = 'png'
            graph.render(filename=png_path, cleanup=True)
            image_paths.append(png_path)
        except Exception as e:
            error_blocks.append((idx, code, str(e)))
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
Generate a unique DOT diagram (digraph G) that visualizes the specific actors, steps, and interactions for this use case. Use only nodes and arrows. No generic diagrams. No advanced formatting. Output only the DOT code, no extra text.
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        if response.text:
            code = response.text.strip().replace('```dot','').replace('```','').strip()
            code = sanitize_dot_code(code)
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
            strict_prompt = f"Given the following business problem: {business_problem}\nAnd this use case: {uc['title']}\nActors: {uc['actors']}\nMain Flow: {uc['main_flow']}\nGenerate a simple DOT digraph G diagram. Use only nodes and arrows. No advanced formatting."
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(strict_prompt)
                if response.text:
                    diagram_code = response.text.strip().replace('```dot','').replace('```','').strip()
                    diagram_code = sanitize_dot_code(diagram_code)
                else:
                    diagram_code = sanitize_dot_code("digraph G { A [label='Actor'] B [label='System'] A -> B }")  # last-resort fallback
            except Exception:
                diagram_code = sanitize_dot_code("digraph G { A [label='Actor'] B [label='System'] A -> B }")  # last-resort fallback
        # Insert or replace diagram in the report
        uc_pattern = re.compile(rf"(\*\*Use Case {uc['idx']}:\*\*.*?\*\*Main Flow:\*\*.*?)(\n\n|\Z)", re.DOTALL)
        match = uc_pattern.search(new_report)
        if match:
            insert_pos = match.end(1)
            after_main_flow = new_report[insert_pos:insert_pos+200]
            dot_match = re.search(r"```dot[\s\S]*?```", after_main_flow)
            if dot_match:
                start = insert_pos + dot_match.start()
                end = insert_pos + dot_match.end()
                new_report = new_report[:start] + f"```dot\n{diagram_code}\n```" + new_report[end:]
            else:
                new_report = new_report[:insert_pos] + f"\n```dot\n{diagram_code}\n```" + new_report[insert_pos:]
    return new_report
def generate_report_and_images(business_problem):
    prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            report_text = response.text if response.text else "No content generated."
            report_text = insert_use_case_diagrams(report_text, business_problem)
            image_paths, error_blocks, fixed_blocks = extract_and_render_dot(report_text, business_problem=business_problem)
            if fixed_blocks:
                for idx, code in fixed_blocks:
                    report_text += f"\n\n**Note:** DOT diagram {idx} was generated using strict AI prompt.\n```dot\n{code}\n```\n"
            if error_blocks:
                for idx, code, err in error_blocks:
                    report_text += f"\n\n**Warning:** DOT diagram {idx} could not be rendered.\nError: {err}\n\n```dot\n{code}\n```\n"
            return report_text, image_paths
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "overloaded" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                    time.sleep(wait_time)
                    continue
                else:
                    return f"API is currently overloaded. Please try again in a few minutes. Error: {error_msg}", []
            else:
                return f"Error generating report: {error_msg}", []
    return "Failed to generate report after multiple attempts. Please try again later.", []
def ensure_dot_diagrams(report):
    keywords = [
        (r"stakeholder.*map", '''```dot\nflowchart TD\n    A[Sponsor] --> B[Project Steering Committee]\n    B --> C[Business Owners]\n    B --> D[IT Leadership]\n    C --> E[Product Management]\n    C --> F[Marketing Department]\n    D --> G[Mobile App Development Team]\n    D --> H[Data Engineering Team]\n    D --> I[Cybersecurity Team]\n    E --> J[Sales Team]\n    F --> K[Customer Service]\n    L[End Users] --> M[External Regulators]\n```'''),
        (r"process.*flow|flow\s*chart|workflow", '''```dot\nflowchart TD\n    A[Customer Opens App] --> B[Login Authentication]\n    B --> C[View Dashboard]\n    C --> D[Check Recommendations]\n    D --> E[Select Product]\n    E --> F[Complete Application]\n    F --> G[Submit for Approval]\n    G --> H[Receive Decision]\n    H --> I[Product/Service Delivered]\n```'''),
        (r"use case.*diagram|use case.*chart|use case.*graph|use case", '''```dot\nflowchart TD\n    Actor1[Customer] -->|Interacts with| System[Mobile Banking App]\n    System -->|Recommends| Offer[Personalized Loan Offer]\n```'''),
        (r"data.*mapping|data.*diagram|data.*chart|data.*flow", '''```dot\nflowchart TD\n    DataSource[Customer Data] --> Engine[Data Analytics Engine]\n    Engine --> Offers[Personalized Loan Offers]\n    Offers --> App[Mobile Banking App]\n```'''),
    ]
    for pattern, template in keywords:
        matches = list(re.finditer(rf"^#+\s*(.*{pattern}.*)$", report, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            section_start = match.end()
            next_300 = report[section_start:section_start+300]
            if '```dot' not in next_300:
                insert_pos = section_start
                report = report[:insert_pos] + '\n' + template + '\n' + report[insert_pos:]
    return report
def generate_report(bp):
    if not bp.strip():
        return "Please enter a business problem first.", "Ready to generate report..."
    status_msg = "Generating report... (this may take a moment)"
    report, _ = generate_report_and_images(bp)
    report = ensure_dot_diagrams(report)
    final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
    return report, final_status
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
    report_output = gr.Markdown(label="Generated Report")
    run_btn.click(generate_report, inputs=[business_problem], outputs=[report_output, status])
demo.launch() 