import gradio as gr
from config import GEMINI_API_KEY, MODEL_NAME
from google import genai
import re
import subprocess
import os
import time
import random

# Set up Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Default prompt template for the full report
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

CRITICAL Mermaid Diagram Requirements:
- Use ONLY this exact syntax for stakeholder maps:
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

- Use ONLY this exact syntax for process flows:
```mermaid
flowchart TD
    A[Customer Opens App] --> B[Login Authentication]
    B --> C[View Dashboard]
    C --> D[Check Loan Recommendations]
    D --> E[Select Loan Product]
    E --> F[Complete Application]
    F --> G[Submit for Approval]
    G --> H[Receive Decision]
    H --> I[Loan Disbursed]
```

- DO NOT use any advanced features like styling, colors, or complex formatting
- Keep diagrams simple with basic rectangles and arrows only
- Test your syntax before outputting

Format each section with a clear Markdown header (e.g., ## 01. Stakeholder Map) and use code blocks for Mermaid diagrams. Make the report clear, structured, and actionable.

Business Problem:
{business_problem}
'''

def extract_and_render_mermaid(md_text, output_dir=OUTPUT_DIR):
    # Find all mermaid code blocks
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", md_text, re.DOTALL)
    image_paths = []
    for idx, code in enumerate(mermaid_blocks, 1):
        mmd_path = os.path.join(output_dir, f"diagram_{idx}.mmd")
        png_path = os.path.join(output_dir, f"diagram_{idx}.png")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(code)
        # Try to call mermaid-cli to generate PNG, but don't fail if not available
        try:
            subprocess.run(["mmdc", "-i", mmd_path, "-o", png_path], check=True, capture_output=True)
            if os.path.exists(png_path):
                image_paths.append(png_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If mmdc is not available, just continue without generating PNG
            print(f"Mermaid CLI not available - diagrams saved as .mmd files only")
            break
    return image_paths

def generate_report_and_images(business_problem):
    prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            report_text = response.text if response.text else "No content generated."
            image_paths = extract_and_render_mermaid(report_text)
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

def gradio_dashboard():
    with gr.Blocks() as demo:
        gr.Markdown("# Business Analysis Report Generator (Agentic AI)")
        gr.Markdown("⚠️ **Note:** If you encounter API overload errors, the system will automatically retry up to 3 times with increasing delays.")
        
        business_problem = gr.Textbox(label="Business Problem / Objective", value="", lines=8, placeholder="Paste your business case or objective here...")
        run_btn = gr.Button("Generate Report")
        status = gr.Textbox(label="Status", value="Ready to generate report...", interactive=False)
        report_output = gr.Markdown(label="Generated Report")
        image_gallery = gr.Gallery(label="Generated Diagrams (PNG)")

        def generate_report(bp):
            if not bp.strip():
                return "Please enter a business problem first.", "Ready to generate report...", []
            
            status_msg = "Generating report... (this may take a moment)"
            report, images = generate_report_and_images(bp)
            final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
            return report, final_status, images

        run_btn.click(generate_report, inputs=[business_problem], outputs=[report_output, status, image_gallery])
    return demo

if __name__ == "__main__":
    gradio_dashboard().launch(share=True, server_name="0.0.0.0", server_port=7860) 