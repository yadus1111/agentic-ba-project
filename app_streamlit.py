import sys
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# Streamlit version of the Agentic BA Dashboard
from dotenv import load_dotenv
load_dotenv()
import os
import re
import time
import base64
import tempfile
import streamlit as st
from config import MODEL_NAME
import google.generativeai as genai
from bs4 import BeautifulSoup, Tag
import markdown
from playwright.sync_api import sync_playwright
import random
import subprocess
import sys
sys.path.append("Mockup_design")
from enhanced_agent import EnhancedBRDAgent

# --- Gemini Model Setup (NEW SDK) ---
# Set up Gemini model using environment variable
try:
    # Check if API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please set it in Streamlit Cloud secrets or your .env file.")
        st.info("To fix this in Streamlit Cloud:\n1. Go to your app settings\n2. Add GEMINI_API_KEY to the secrets\n3. Redeploy the app")
        st.stop()
    
    model = genai.GenerativeModel(MODEL_NAME)
    st.success("✅ Gemini AI model initialized successfully")
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini AI: {str(e)}")
    st.stop()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Utility Functions (copied from app_playwright.py) ---
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
        r'style\s+', r'subgraph\s+', r'classDef\s+', r'click\s+', r'linkStyle\s+', r'end\s+', r'class\s+',
        r'%%', r'-->|', r'---|', r'==>', r'-.->', r'==>', r':::', r'{{', r'}}', r'\(\(', r'\)\)',
        r'\[\(', r'\)\]', r'\(\[', r'\]\)'
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
            mmdc_paths = [
                "mmdc", "/usr/local/bin/mmdc", "/usr/bin/mmdc", r"C:\\Users\\acer\\AppData\\Roaming\\npm\\mmdc.cmd"
            ]
            rendered = False
            for mmdc_path in mmdc_paths:
                try:
                    subprocess.run([
                        mmdc_path, "-i", mmd_path, "-o", png_path,
                        "--theme", "neutral",
                        "--backgroundColor", "white",
                        "--width", "2000",
                        "--height", "900",
                        "--scale", "3"
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
                    if os.path.exists(png_path):
                        image_paths.append(png_path)
                        rendered = True
                        break
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue  # Suppress all errors and warnings
            if not rendered:
                error_blocks.append((idx, code, "Mermaid CLI not available - diagrams will be rendered in browser"))
        except Exception as e:
            error_blocks.append((idx, code, f"Could not save file: {str(e)}"))
        fixed_blocks.append((idx, code))
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
    except Exception:
        return None

def insert_use_case_diagrams(report_text, business_problem):
    use_cases = extract_use_case_details(report_text)
    if not use_cases:
        return report_text
    new_report = report_text
    for uc in use_cases:
        diagram_code = generate_use_case_diagram(business_problem, uc)
        if not diagram_code:
            diagram_code = "Diagram could not be generated for this use case."
        uc_pattern = re.compile(rf"(\*\*Use Case {uc['idx']}:\*\*.*?\*\*Main Flow:\*\*.*?)(\n\n|\Z)", re.DOTALL)
        match = uc_pattern.search(new_report)
        if match:
            insert_pos = match.end(1)
            after_main_flow = new_report[insert_pos:insert_pos+200]
            mermaid_match = re.search(r"```mermaid[\s\S]*?```", after_main_flow)
            if mermaid_match:
                start = insert_pos + mermaid_match.start()
                end = insert_pos + mermaid_match.end()
                new_report = new_report[:start] + f"```mermaid\n{diagram_code}\n```" + new_report[end:]
            else:
                new_report = new_report[:insert_pos] + f"\n```mermaid\n{diagram_code}\n```" + new_report[insert_pos:]
    return new_report

REPORT_PROMPT_TEMPLATE = '''
You are an expert Business Analyst specializing in banking and fintech. According to the business problem/objective, generate a complete business analysis report in Markdown format. The report must include:
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
- Make the report visually structured and easy to read.
- Do NOT output any generic template content—make all content specific to the provided business problem and use cases.

Business Problem:
{business_problem}
'''

def generate_report_and_images(business_problem):
    try:
        # Check if model is properly initialized
        if not model:
            return "❌ Gemini AI model not initialized. Please check your API key.", []
        
        st.info("📝 Preparing report prompt...")
        prompt = REPORT_PROMPT_TEMPLATE.format(business_problem=business_problem)
        
        st.info("🤖 Sending request to Gemini AI...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                st.info(f"🔄 Attempt {attempt + 1} of {max_retries}...")
                response = model.generate_content(prompt)
                
                if not response or not response.text:
                    return "❌ No content generated from Gemini AI. Please try again.", []
                
                st.info("📄 Processing generated content...")
                report_text = response.text
                report_text = insert_use_case_diagrams(report_text, business_problem)
                image_paths, error_blocks, fixed_blocks = extract_and_render_mermaid(report_text, business_problem=business_problem)
                
                st.success("✅ Report generated successfully!")
                return report_text, image_paths
                
            except Exception as e:
                error_msg = str(e)
                st.warning(f"⚠️ Attempt {attempt + 1} failed: {error_msg}")
                
                if "503" in error_msg or "overloaded" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                        st.info(f"⏳ Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"❌ API is currently overloaded. Please try again in a few minutes. Error: {error_msg}", []
                else:
                    return f"❌ Error generating report: {error_msg}", []
        
        return "❌ Failed to generate report after multiple attempts. Please try again later.", []
        
    except Exception as e:
        return f"❌ Unexpected error in report generation: {str(e)}", []

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_sticker_images(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        if isinstance(img, Tag):
            src = img.get('src')
            if src and isinstance(src, str) and not src.startswith('data:image/png;base64'):
                img.decompose()
    return str(soup)

def remove_llm_intro_paragraph(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    first_p = soup.find('p')
    if first_p and isinstance(first_p, Tag):
        text = first_p.get_text().strip().lower()
        if (
            text.startswith('as an expert business analyst') or
            text.startswith('as a business analyst') or
            'i have prepared a comprehensive report' in text or
            text.startswith('here is a complete business analysis report') or
            text.startswith('here is a business analysis report') or
            text.startswith('here is the business analysis report') or
            text.startswith('this is a complete business analysis report')
        ):
            first_p.decompose()
    return str(soup)

def wrap_html_with_css(html_content):
    css = '''<style>\n.html-report h1, .html-report h2, .html-report h3 {\n    color: #22223b;\n    font-weight: bold;\n    font-family: 'Times New Roman', Times, serif;\n    margin-top: 1.5em;\n    margin-bottom: 0.5em;\n}\n.html-report h2 {\n    font-size: 2em;\n}\n.html-report h3 {\n    font-size: 1.3em;\n}\n.html-report ul, .html-report ol {\n    margin-left: 2.2em;\n    margin-bottom: 1.2em;\n    font-size: 0.97em;\n    font-family: 'Times New Roman', Times, serif;\n}\n.html-report li {\n    color: #22223b;\n    font-size: 0.97em;\n    margin-bottom: 0.25em;\n    font-family: 'Times New Roman', Times, serif;\n    padding-left: 0.2em;\n}\n.html-report p {\n    font-family: 'Times New Roman', Times, serif;\n    font-size: 1.01em;\n    margin-bottom: 0.7em;\n    color: #22223b;\n}\n.html-report table, .html-report th, .html-report td {\n    border: 1.5px solid #22223b !important;\n    border-collapse: collapse !important;\n    padding: 7px 8px !important;\n    font-size: 0.98em !important;\n    background: #fff !important;\n    word-break: break-word !important;\n    overflow-wrap: break-word !important;\n    max-width: 120px !important;\n    font-family: 'Times New Roman', Times, serif;\n}\n.html-report th, .html-report td {\n    word-break: break-word !important;\n    overflow-wrap: break-word !important;\n    max-width: 120px !important;\n}\n.html-report table {\n    display: block;\n    overflow-x: auto;\n    width: 100% !important;\n    max-width: 100% !important;\n    margin-left: auto;\n    margin-right: auto;\n}\n.html-report th {\n    background: #fff !important;\n    font-weight: bold !important;\n    color: #22223b !important;\n}\n.html-report tr:nth-child(even) {\n    background: #f3f4f6 !important;\n}\n.html-report tr:hover {\n    background: #e5e5e5 !important;\n}\n.html-report img {\n    border: 1.5px solid #22223b;\n    border-radius: 10px;\n    margin: 18px auto;\n    display: block;\n    max-width: 95vw;\n    max-height: 80vh;\n    min-width: 400px;\n    min-height: 200px;\n    object-fit: contain;\n    background: #fff;\n}\n.html-report code {\n    background-color: #f1f5f9;\n    padding: 2px 6px;\n    border-radius: 4px;\n    font-family: 'Courier New', monospace;\n    font-size: 0.9em;\n    color: #22223b;\n}\n.html-report pre {\n    background-color: #f8fafc;\n    border: 1px solid #e2e8f0;\n    border-radius: 8px;\n    padding: 15px;\n    overflow-x: auto;\n    margin: 15px 0;\n}\n.html-report pre code {\n    background: none;\n    padding: 0;\n    color: #22223b;\n}\n</style>'''
    return f'<html><head>{css}</head><body>{html_content}</body></html>'

def html_to_pdf_with_playwright(html_content, output_pdf_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="load")
        page.pdf(path=output_pdf_path, format="A4", print_background=True, margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"})
        browser.close()

# --- Streamlit UI for Agentic BA Dashboard ---
def main():
    st.set_page_config(page_title="Agentic BA Dashboard", layout="wide")
    st.title("Agentic BA Dashboard")
    st.markdown("Welcome to your AI-powered business analysis system!")

    business_problem = st.text_area(
        "Business Problem / Objective",
        value="",
        height=180,
        placeholder="Paste your business case or objective here..."
    )

    if 'report_data' not in st.session_state:
        st.session_state['report_data'] = {"html": "", "business_problem": ""}
    if 'pdf_path' not in st.session_state:
        st.session_state['pdf_path'] = None
    # Initialize BA agent only once
    if 'ba_agent' not in st.session_state:
        st.session_state['ba_agent'] = EnhancedBRDAgent()

    if st.button("Generate Report", type="primary"):
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Starting report generation...")
            progress_bar.progress(10)
            
            report, images = generate_report_and_images(business_problem)
            
            progress_bar.progress(100)
            status_text.text("✅ Report generation completed!")
            
        except Exception as e:
            st.error(f"❌ Error during report generation: {str(e)}")
            return
        finally:
            # Clear the progress indicators
            progress_bar.empty()
            status_text.empty()
            for idx, img_path in enumerate(images, 1):
                if os.path.exists(img_path):
                    with open(img_path, "rb") as img_file:
                        b64 = base64.b64encode(img_file.read()).decode("utf-8")
                    img_tag = f'<img src="data:image/png;base64,{b64}" style="max-width:100%; margin: 20px 0;" />'
                    report = re.sub(r"```mermaid[\s\S]*?```", img_tag, report, count=1)
            html_report = markdown.markdown(report, extensions=['tables', 'fenced_code'])
            html_report = f'<div class="html-report">{html_report}</div>'
            html_report = remove_emojis(html_report)
            html_report = remove_llm_intro_paragraph(html_report)
            st.session_state['report_data'] = {"html": html_report, "business_problem": business_problem}
            st.session_state['pdf_path'] = None

    # PDF buttons above the report
    if st.session_state['report_data']['html']:
        col_pdf1, col_pdf2 = st.columns([1, 1])
        with col_pdf1:
            if st.button("Download PDF"):
                with st.spinner("Generating PDF..."):
                    html_clean = remove_sticker_images(st.session_state['report_data']['html'])
                    html_clean = remove_emojis(html_clean)
                    html_clean = remove_llm_intro_paragraph(html_clean)
                    html_final = wrap_html_with_css(html_clean)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"business_analysis_report_{timestamp}.pdf"
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    html_to_pdf_with_playwright(html_final, temp_file.name)
                    st.session_state['pdf_path'] = temp_file.name
        with col_pdf2:
            if st.session_state['pdf_path']:
                with open(st.session_state['pdf_path'], "rb") as f:
                    st.download_button(
                        label="Download PDF File",
                        data=f,
                        file_name="business_analysis_report.pdf",
                        mime="application/pdf"
                    )
        st.markdown("### Generated Report")
        st.components.v1.html(st.session_state['report_data']['html'], height=900, scrolling=True)

        # --- Mockup Generation Integration ---
        if st.button("Generate Mockup"):
            with st.spinner("Generating HTML mockup..."):
                try:
                    brd_text = st.session_state['report_data']['business_problem']
                    agent = st.session_state['ba_agent']
                    
                    # Debug: Check if agent is properly initialized
                    if not agent.client:
                        st.error("❌ Gemini AI client not available. Please check your API key.")
                        return
                    
                    st.info(f"📝 Analyzing BRD content...")
                    app_type = agent.analyze_brd_content(brd_text)
                    st.info(f"🎯 Detected app type: {app_type}")
                    
                    st.info(f"🎨 Generating UI schema...")
                    schema = agent.generate_ui_schema(brd_text, app_type)
                    if not schema:
                        st.error("❌ Failed to generate UI schema")
                        return
                    
                    st.info(f"🌐 Converting to HTML mockup...")
                    html_content = agent.convert_schema_to_html(schema, app_type, brd_text)
                    if not html_content:
                        st.error("❌ Failed to convert schema to HTML")
                        return
                    
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    outputs = agent.save_outputs(schema, html_content, app_type, timestamp)
                    
                    if outputs and outputs.get('html'):
                        st.success(f"✅ Mockup generated successfully!")
                        
                        # Display the HTML mockup directly in Streamlit
                        st.subheader("Generated HTML Mockup Preview")
                        st.components.v1.html(html_content, height=600, scrolling=True)
                        
                        # Download button
                        st.download_button(
                            label="Download HTML Mockup",
                            data=html_content,
                            file_name=f"{app_type}_mockup_{timestamp}.html",
                            mime="text/html"
                        )
                    else:
                        st.error("❌ Failed to save mockup outputs")
                        
                except Exception as e:
                    st.error(f"❌ Error generating mockup: {str(e)}")
                    st.info("💡 This might be due to API limitations on Streamlit Cloud. Try running locally for full functionality.")

if __name__ == "__main__":
    main() 