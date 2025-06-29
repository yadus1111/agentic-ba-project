import os
import gradio as gr
from agents import AGENTS, client
from config import MODEL_NAME

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DEFAULT_BUSINESS_PROBLEM = '''
Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking
Despite having multiple loan products (e.g., home loans, personal loans, auto loans, educational loans, foneloan), customer uptake through the mobile banking app remains low. However, data indicates high mobile app engagement for other features like utility payments, fund transfers, and balance inquiries.
The bank wants to use its available data sources to personalize and recommend suitable loan products through its mobile banking app, to increase conversions and enhance customer engagement.
Objective for the BA:
Design a solution that uses customer data to personalize and improve the visibility, relevance, and uptake of loan products on the mobile Banking app.
'''

DELIVERABLES = [
    ("01_Stakeholder_Map.md", AGENTS["process_modeler"].system_message + "\n\nTask: Create a stakeholder map in Mermaid format for the above business problem."),
    ("02_Process_Flow.md", AGENTS["process_modeler"].system_message + "\n\nTask: Create a process flow diagram in Mermaid format for the new loan uptake journey in the mobile app."),
    ("03_Business_Requirement_Document.md", AGENTS["business_analyst"].system_message + "\n\nTask: Write a Business Requirement Document (BRD) for the above business problem."),
    ("04_Functional_Requirement_Specification.md", AGENTS["business_analyst"].system_message + "\n\nTask: Write a Functional Requirement Specification (FRS), including Non-Functional Requirements."),
    ("05_Use_Cases_and_Scenarios.md", AGENTS["use_case"].system_message + "\n\nTask: Develop use case diagrams and detailed scenarios for the three specified cases."),
    ("06_Data_Mapping_Sheet.md", AGENTS["data_analyst"].system_message + "\n\nTask: Create a data mapping sheet and data requirements analysis."),
    ("07_Functional_Scope_Summary.md", AGENTS["business_analyst"].system_message + "\n\nTask: Write a functional scope summary (in/out of scope)."),
    ("08_Suggested_KPIs.md", AGENTS["kpi"].system_message + "\n\nTask: Suggest KPIs and success metrics for the project."),
    ("README.md", AGENTS["technical_writer"].system_message + "\n\nTask: Write a README explaining the generated files.")
]

REPORT_PROMPT_TEMPLATE = '''
You are an expert Business Analyst specializing in banking and fintech. Given the following business problem/objective, generate a complete business analysis report in Markdown format. The report must include:

1. Stakeholder Map (as a Mermaid diagram in a code block)
2. Process Flow of the new loan uptake journey (as a Mermaid diagram in a code block)
3. Business Requirement Document (BRD)
4. Functional Requirement Specification (FRS), including Non-Functional Requirements
5. Use Case Diagrams and detailed Scenarios for three specific cases
6. Data Mapping Sheet and Data Requirements Analysis (as a Markdown table)
7. Functional Scope Summary (In/Out of Scope)
8. Suggested KPIs for success measurement

IMPORTANT: For the Stakeholder Map and Process Flow, ALWAYS use the following exact Mermaid code blocks, only changing the section title to match the business case. Do NOT generate any other Mermaid code or syntax. This ensures compatibility with Mermaid version 11.5.0.

Stakeholder Map:
```mermaid
flowchart TD
    A[Sponsor] --> B[Project Steering Committee]
    B --> C[Business Owners]
    B --> D[IT Leadership]
    C --> E[Product Management]
    C --> F[Marketing Department]
    D --> G[Mobile App Development Team]
    D --> H[Data Engineering Team]
    D --> I[Cybersecurity Team]
    E --> J[Sales Team]
    F --> K[Customer Service]
    L[End Users] --> M[External Regulators]
```

Process Flow:
```mermaid
flowchart TD
    A[Customer Opens App] --> B[Login Authentication]
    B --> C[View Dashboard]
    C --> D[Check Recommendations]
    D --> E[Select Product]
    E --> F[Complete Application]
    F --> G[Submit for Approval]
    G --> H[Receive Decision]
    H --> I[Product/Service Delivered]
```

- DO NOT use any advanced features like styling, colors, or complex formatting
- Keep diagrams simple with basic rectangles and arrows only
- Test your syntax before outputting

Format each section with a clear Markdown header (e.g., ## 01. Stakeholder Map) and use code blocks for Mermaid diagrams. Make the report clear, structured, and actionable.

Business Problem:
{business_problem}
'''

def call_agent(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text if response.text else "No content generated"
    except Exception as e:
        return f"Error generating content: {str(e)}"

def run_multiagent_workflow(business_problem, progress=gr.Progress(track_tqdm=True)):
    status_msgs = []
    for idx, (filename, agent_prompt) in enumerate(DELIVERABLES, 1):
        status_msgs.append(f"Generating {filename}...")
        full_prompt = f"{business_problem}\n\n{agent_prompt}"
        content = call_agent(full_prompt)
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)
        status_msgs.append(f"Saved: {filename}")
        progress(idx / len(DELIVERABLES))
    status_msgs.append("All deliverables generated in the 'output' directory.")
    return "\n".join(status_msgs)

def list_output_files():
    files = []
    if os.path.exists(OUTPUT_DIR):
        for fname in os.listdir(OUTPUT_DIR):
            fpath = os.path.join(OUTPUT_DIR, fname)
            if os.path.isfile(fpath):
                files.append(fpath)
    return files

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def generate_full_report(business_problem):
    prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        report_text = response.text if response.text else "No content generated."
        return report_text
    except Exception as e:
        return f"Error generating report: {str(e)}"

def gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Agentic BA Multi-Agent System (Gemini)")
        business_problem = gr.Textbox(label="Business Problem / Objective", value=DEFAULT_BUSINESS_PROBLEM, lines=8)
        run_btn = gr.Button("Generate All Deliverables")
        full_report_btn = gr.Button("Generate Full Report")
        status = gr.Textbox(label="Status / Progress", interactive=False, lines=8)
        file_list = gr.Dropdown(choices=list_output_files(), label="Select Output File", interactive=True, allow_custom_value=True)
        file_content = gr.Textbox(label="File Content", lines=20, interactive=False)
        full_report_output = gr.Markdown(label="Full Report Output")
        download_btn = gr.File(label="Download Selected File", interactive=False)

        def run_and_update(bp):
            msg = run_multiagent_workflow(bp)
            return msg, list_output_files(), "", None

        def show_file_content(selected):
            if selected and os.path.exists(selected):
                content = read_file_content(selected)
                return content, selected
            return "", None

        def run_full_report(bp):
            report = generate_full_report(bp)
            return report

        run_btn.click(run_and_update, inputs=[business_problem], outputs=[status, file_list, file_content, download_btn])
        file_list.change(show_file_content, inputs=file_list, outputs=[file_content, download_btn])
        full_report_btn.click(run_full_report, inputs=[business_problem], outputs=[full_report_output])
    return demo

if __name__ == "__main__":
    gradio_interface().launch() 