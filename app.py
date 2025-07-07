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
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import re
import hashlib
from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

# Set up Gemini model using environment variable
model = genai.GenerativeModel(MODEL_NAME)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Default prompt template for the full report
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
                            mmdc_path, "-i", mmd_path, "-o", png_path,
                            "--theme", "neutral",
                            "--backgroundColor", "white",
                            "--width", "2000",
                            "--height", "900",
                            "--scale", "3"
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

def bold_label_phrases(text):
    # Bold any 'Label: value' style phrase (e.g., 'Functional Dependency: ...')
    return re.sub(r'(\b[\w\s]+:)', r'<b>\1</b>', text)

def remove_emojis(text):
    # Remove a wide range of emoji and sticker unicode characters
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

def remove_duplicate_sections(html_content):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    seen_headers = set()
    new_content = []
    current_section = []
    current_header = None
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'img']):
        if isinstance(element, Tag) and element.name in ['h1', 'h2', 'h3']:
            header_text = element.get_text(strip=True)
            if header_text in seen_headers:
                current_header = None  # skip this header and its content
            else:
                seen_headers.add(header_text)
                if current_section:
                    new_content.extend(current_section)
                current_section = [str(element)]
                current_header = header_text
        else:
            if current_header is not None:
                current_section.append(str(element))
    if current_section:
        new_content.extend(current_section)
    # Wrap in a div if needed
    return '<div class="html-report">' + '\n'.join(new_content) + '</div>'

def advanced_deduplicate_content(html_content):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    new_content = []
    text_groups = {}
    diagram_hashes = set()
    # Group similar text by normalized substring containment
    def add_to_group(text, element):
        norm = ' '.join(text.split()).lower()
        for key in list(text_groups.keys()):
            if norm in key or key in norm:
                # Keep the longer one
                if len(norm) > len(key):
                    text_groups[norm] = element
                    del text_groups[key]
                return
        text_groups[norm] = element
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'img']):
        if isinstance(element, Tag):
            # Deduplicate diagrams by image content hash
            src = element.get('src') if element.name == 'img' else None
            if src and isinstance(src, str) and src.startswith('data:image'):
                try:
                    img_data = src.split(',')[1]
                    img_bytes = img_data.encode('utf-8')
                    img_hash = hashlib.md5(img_bytes).hexdigest()
                    if img_hash in diagram_hashes:
                        continue
                    diagram_hashes.add(img_hash)
                    new_content.append(str(element))
                except Exception:
                    new_content.append(str(element))
            # Advanced deduplication for paragraphs and list items
            elif element.name in ['p', 'li']:
                text = element.get_text(strip=True)
                add_to_group(text, element)
            else:
                new_content.append(str(element))
    # Add only the best (longest) occurrence for each text group
    for elem in text_groups.values():
        new_content.append(str(elem))
    return '<div class="html-report">' + '\n'.join(new_content) + '</div>'

def remove_duplicate_content(html_content):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    new_content = []
    seen_text = set()
    seen_diagrams = set()
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'img']):
        if isinstance(element, Tag):
            # Deduplicate diagrams (img with src containing 'diagram')
            if element.name == 'img' and 'diagram' in (element.get('src') or ''):
                src = element.get('src')
                if src in seen_diagrams:
                    continue
                seen_diagrams.add(src)
                new_content.append(str(element))
            # Deduplicate paragraphs and list items
            elif element.name in ['p', 'li']:
                norm_text = ' '.join(element.get_text(strip=True).split()).lower()
                if norm_text in seen_text:
                    continue
                seen_text.add(norm_text)
                new_content.append(str(element))
            # Always keep headers, tables, lists, etc.
            else:
                new_content.append(str(element))
    return '<div class="html-report">' + '\n'.join(new_content) + '</div>'

def generate_pdf_from_html(html_content, business_problem):
    try:
        html_content = remove_duplicate_sections(html_content)
        html_content = remove_emojis(html_content)
        html_content = advanced_deduplicate_content(html_content)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        # Mirror Gradio dashboard CSS styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1e3a8a'), spaceAfter=12, alignment=TA_CENTER, fontName='Times-Bold', leading=26)
        heading1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1e3a8a'), spaceAfter=8, spaceBefore=18, fontName='Times-Bold', leading=22, leftIndent=0)
        heading2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=15, textColor=colors.HexColor('#1e3a8a'), spaceAfter=6, spaceBefore=14, fontName='Times-Bold', leading=18, leftIndent=0)
        heading3_style = ParagraphStyle('Heading3', parent=styles['Heading3'], fontSize=13, textColor=colors.HexColor('#1e3a8a'), spaceAfter=4, spaceBefore=10, fontName='Times-Bold', leading=15, leftIndent=0)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#22223b'), spaceAfter=3, alignment=TA_JUSTIFY, leading=15, leftIndent=0, rightIndent=0, fontName='Times-Roman')
        list_style = ParagraphStyle('List', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#22223b'), spaceAfter=2, leftIndent=22, leading=14, fontName='Times-Roman')
        bullet_style = ParagraphStyle('Bullet', parent=list_style, leftIndent=32, fontSize=11, textColor=colors.HexColor('#1e3a8a'), spaceAfter=2, fontName='Times-Roman')
        # Table style to match dashboard
        table_header_bg = colors.HexColor('#e0e7ff')
        table_header_text = colors.HexColor('#1e3a8a')
        table_row_bg = [colors.white, colors.HexColor('#f3f4f6')]
        table_border = colors.HexColor('#a5b4fc')
        # Spacers for consistent vertical spacing
        h1_spacer = Spacer(1, 8)
        h2_spacer = Spacer(1, 6)
        h3_spacer = Spacer(1, 4)
        table_img_spacer = Spacer(1, 4)
        list_spacer = Spacer(1, 3)
        para_spacer = Spacer(1, 3)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        available_width = A4[0] - 2*cm
        min_col_width = 1.2*cm
        max_col_width = 3.2*cm
        temp_img_paths = []
        story = [Paragraph(f"""
        <para align='center'>
        <font size='22' color='#1e3a8a'><b>Business Analysis Report</b></font><br/>
        <font size='11' color='#374151'>Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}</font><br/>
        <font size='9' color='#374151'><i>Business Problem: {business_problem[:100]}{'...' if len(business_problem) > 100 else ''}</i></font>
        </para>
        """, title_style), Spacer(1, 8)]
        section_block = []
        def flush_section():
            if section_block:
                story.append(KeepTogether(section_block[:]))
                section_block.clear()
        def render_list(element, level=0):
            items = []
            for li in element.find_all('li', recursive=False):
                li_text = li.get_text()
                li_text = re.sub(r'(Measure:)', r'<b>\1</b>', li_text)
                li_text = re.sub(r'(Target:)', r'<b>\1</b>', li_text)
                bullet_indent = 32 + level*14
                bullet_style_nested = ParagraphStyle(f'BulletLevel{level}', parent=bullet_style, leftIndent=bullet_indent)
                items.append(Paragraph(f"• {li_text}", bullet_style_nested))
                for sublist in li.find_all(['ul', 'ol'], recursive=False):
                    items.extend(render_list(sublist, level+1))
            return items
        def extract_lists_from_paragraph(text):
            lines = text.split('\n')
            items = []
            current_list = []
            current_type = None
            for line in lines:
                line = line.strip()
                if re.match(r'^(\* |- )', line):
                    if current_type != 'ul' and current_list:
                        items.append(('ol', current_list))
                        current_list = []
                    current_type = 'ul'
                    current_list.append(line[2:].strip())
                elif re.match(r'^\d+\. ', line):
                    if current_type != 'ol' and current_list:
                        items.append(('ul', current_list))
                        current_list = []
                    current_type = 'ol'
                    current_list.append(line[line.find('.')+1:].strip())
                else:
                    if current_list:
                        items.append((current_type, current_list))
                        current_list = []
                        current_type = None
                    if line:
                        items.append(('p', line))
            if current_list:
                items.append((current_type, current_list))
            return items
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li', 'table', 'img']):
            if isinstance(element, Tag):
                if element.name == 'h1':
                    flush_section()
                    section_block.append(Paragraph(bold_label_phrases(element.get_text()), heading1_style))
                    section_block.append(h1_spacer)
                elif element.name == 'h2':
                    flush_section()
                    section_block.append(Paragraph(bold_label_phrases(element.get_text()), heading2_style))
                    section_block.append(h2_spacer)
                elif element.name == 'h3':
                    flush_section()
                    section_block.append(Paragraph(bold_label_phrases(element.get_text()), heading3_style))
                    section_block.append(h3_spacer)
                elif element.name == 'p':
                    if element.get_text().strip():
                        p_text = element.get_text()
                        for typ, content in extract_lists_from_paragraph(p_text):
                            if typ == 'ul':
                                for b in content:
                                    b = re.sub(r'(Measure:)', r'<b>\\1</b>', b)
                                    b = re.sub(r'(Target:)', r'<b>\\1</b>', b)
                                    bullet_para = Paragraph(f"• {b}", bullet_style)
                                    section_block.append(bullet_para)
                                section_block.append(list_spacer)
                            elif typ == 'ol':
                                for idx, b in enumerate(content, 1):
                                    b = re.sub(r'(Measure:)', r'<b>\\1</b>', b)
                                    b = re.sub(r'(Target:)', r'<b>\\1</b>', b)
                                    bullet_para = Paragraph(f"{idx}. {b}", bullet_style)
                                    section_block.append(bullet_para)
                                section_block.append(list_spacer)
                            elif typ == 'p':
                                b = re.sub(r'(Measure:)', r'<b>\\1</b>', content)
                                b = re.sub(r'(Target:)', r'<b>\\1</b>', b)
                                section_block.append(Paragraph(bold_label_phrases(b), normal_style))
                                section_block.append(para_spacer)
                elif element.name in ['ul', 'ol']:
                    items = render_list(element, level=0)
                    for para in items:
                        section_block.append(para)
                    section_block.append(list_spacer)
                elif element.name == 'table':
                    table_data = []
                    for row in element.find_all('tr'):
                        row_data = []
                        for cell in row.find_all(['td', 'th']):
                            cell_text = bold_label_phrases(cell.get_text().strip())
                            para = Paragraph(cell_text, normal_style)
                            row_data.append(para)
                        if row_data:
                            table_data.append(row_data)
                    if table_data:
                        num_cols = len(table_data[0])
                        max_lengths = [max(len(str(row[i].getPlainText())) for row in table_data) for i in range(num_cols)]
                        total_length = sum(max_lengths)
                        col_widths = []
                        for l in max_lengths:
                            w = max(min_col_width, min(max_col_width, (l/total_length)*available_width if total_length else available_width/num_cols))
                            col_widths.append(w)
                        scale = available_width / sum(col_widths)
                        col_widths = [w*scale for w in col_widths]
                        for i in range(len(col_widths)):
                            col_widths[i] = max(min_col_width, min(max_col_width, col_widths[i]))
                        table_font_size = 10 if num_cols <= 6 else 8 if num_cols <= 8 else 7
                        for row in table_data:
                            for cell in row:
                                cell.style.fontSize = table_font_size
                        table = Table(table_data, colWidths=col_widths, repeatRows=1)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
                            ('TEXTCOLOR', (0, 0), (-1, 0), table_header_text),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), table_font_size),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                            ('TOPPADDING', (0, 0), (-1, 0), 5),
                            ('LEFTPADDING', (0, 0), (-1, 0), 3),
                            ('RIGHTPADDING', (0, 0), (-1, 0), 3),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#22223b')),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
                            ('FONTSIZE', (0, 1), (-1, -1), table_font_size),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                            ('TOPPADDING', (0, 1), (-1, -1), 4),
                            ('LEFTPADDING', (0, 1), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 1), (-1, -1), 3),
                            ('GRID', (0, 0), (-1, -1), 1, table_border),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), table_row_bg),
                            ('WORDWRAP', (0, 0), (-1, -1), True),
                            ('LEADING', (0, 0), (-1, -1), table_font_size + 2),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ]))
                        section_block.append(table)
                        section_block.append(table_img_spacer)
                elif element.name == 'img':
                    src = element.get('src')
                    if src and isinstance(src, str) and src.startswith('data:image'):
                        import base64, uuid
                        img_data = src.split(',')[1]
                        img_bytes = base64.b64decode(img_data)
                        unique_id = str(uuid.uuid4())[:8]
                        temp_img_path = os.path.join(OUTPUT_DIR, f"temp_img_{unique_id}.png")
                        with open(temp_img_path, 'wb') as f:
                            f.write(img_bytes)
                        temp_img_paths.append(temp_img_path)
                        if os.path.exists(temp_img_path) and os.path.getsize(temp_img_path) > 0:
                            from PIL import Image as PILImage
                            pil_img = PILImage.open(temp_img_path)
                            orig_w, orig_h = pil_img.size
                            max_img_width = available_width * 0.6
                            max_img_height = 10*cm
                            aspect = orig_w / orig_h
                            if (max_img_width / aspect) <= max_img_height:
                                img_width = max_img_width
                                img_height = max_img_width / aspect
                            else:
                                img_height = max_img_height
                                img_width = max_img_height * aspect
                            img = Image(temp_img_path, width=img_width, height=img_height)
                            img.hAlign = 'CENTER'
                            section_block.append(img)
                            section_block.append(table_img_spacer)
                        else:
                            section_block.append(Paragraph("[Diagram - Image creation failed]", normal_style))
                # End of element handling
        flush_section()
        doc.build(story)
        for path in temp_img_paths:
            try:
                os.remove(path)
            except Exception:
                pass
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None

def ensure_mermaid_diagrams(report):
    mermaid_pattern = r'```mermaid\s*\n(.*?)```'
    mermaid_blocks = re.findall(mermaid_pattern, report, re.DOTALL)
    if not mermaid_blocks:
        return report
    diagram_html = ""
    for i, code in enumerate(mermaid_blocks):
        code = code.strip()
        if not code or 'flowchart' not in code:
            continue
        diagram_id = f"mermaid-diagram-{i}"
        diagram_html += f"""
        <div style=\"margin: 20px 0; padding: 20px; background: #f8fafc; border-radius: 10px; border: 2px solid #e0e7ff; text-align: center;\">
            <div class=\"mermaid\" id=\"{diagram_id}\">
{code}
            </div>
        </div>
        """
    if diagram_html:
        mermaid_script = """
        <script src=\"https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js\"></script>
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
        first_replacement = mermaid_script + diagram_html
        report = re.sub(mermaid_pattern, first_replacement, report, count=1)
        remaining_diagrams = diagram_html.split('<div style="margin: 20px 0;')[1:]
        for diagram in remaining_diagrams:
            diagram_html_full = '<div style="margin: 20px 0;' + diagram
            report = re.sub(mermaid_pattern, diagram_html_full, report, count=1)
    return report

# Playwright-based PDF export
# Requires: pip install playwright && python -m playwright install

def html_to_pdf_with_playwright(html_content, output_pdf_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="load")
        # Set small margins (1cm on all sides)
        page.pdf(path=output_pdf_path, format="A4", print_background=True, margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"})
        browser.close()

def remove_sticker_images(html_content):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        if isinstance(img, Tag):
            src = img.get('src')
            if src and isinstance(src, str) and not src.startswith('data:image/png;base64'):
                img.decompose()
    return str(soup)

def wrap_html_with_css(html_content):
    css = '''<style>\n.html-report h1, .html-report h2, .html-report h3 {\n    color: #22223b;\n    font-weight: bold;\n    font-family: 'Times New Roman', Times, serif;\n    margin-top: 1.5em;\n    margin-bottom: 0.5em;\n}\n.html-report h2 {\n    font-size: 2em;\n}\n.html-report h3 {\n    font-size: 1.3em;\n}\n.html-report ul, .html-report ol {\n    margin-left: 2.2em;\n    margin-bottom: 1.2em;\n    font-size: 0.97em;\n    font-family: 'Times New Roman', Times, serif;\n}\n.html-report li {\n    color: #22223b;\n    font-size: 0.97em;\n    margin-bottom: 0.25em;\n    font-family: 'Times New Roman', Times, serif;\n    padding-left: 0.2em;\n}\n.html-report p {\n    font-family: 'Times New Roman', Times, serif;\n    font-size: 1.01em;\n    margin-bottom: 0.7em;\n    color: #22223b;\n}\n.html-report table, .html-report th, .html-report td {\n    border: 1.5px solid #22223b !important;\n    border-collapse: collapse !important;\n    padding: 7px 8px !important;\n    font-size: 0.98em !important;\n    background: #fff !important;\n    word-break: break-word !important;\n    overflow-wrap: break-word !important;\n    max-width: 120px !important;\n    font-family: 'Times New Roman', Times, serif;\n}\n.html-report th, .html-report td {\n    word-break: break-word !important;\n    overflow-wrap: break-word !important;\n    max-width: 120px !important;\n}\n.html-report table {\n    display: block;\n    overflow-x: auto;\n    width: 100% !important;\n    max-width: 100% !important;\n    margin-left: auto;\n    margin-right: auto;\n}\n.html-report th {\n    background: #fff !important;\n    font-weight: bold !important;\n    color: #22223b !important;\n}\n.html-report tr:nth-child(even) {\n    background: #f3f4f6 !important;\n}\n.html-report tr:hover {\n    background: #e5e5e5 !important;\n}\n.html-report img {\n    border: 1.5px solid #22223b;\n    border-radius: 10px;\n    margin: 18px auto;\n    display: block;\n    max-width: 95vw;\n    max-height: 80vh;\n    min-width: 400px;\n    min-height: 200px;\n    object-fit: contain;\n    background: #fff;\n}\n.html-report code {\n    background-color: #f1f5f9;\n    padding: 2px 6px;\n    border-radius: 4px;\n    font-family: 'Courier New', monospace;\n    font-size: 0.9em;\n    color: #22223b;\n}\n.html-report pre {\n    background-color: #f8fafc;\n    border: 1px solid #e2e8f0;\n    border-radius: 8px;\n    padding: 15px;\n    overflow-x: auto;\n    margin: 15px 0;\n}\n.html-report pre code {\n    background: none;\n    padding: 0;\n    color: #22223b;\n}\n</style>'''
    return f'<html><head>{css}</head><body>{html_content}</body></html>'

def remove_llm_intro_paragraph(html_content):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove the first <p> if it matches the LLM intro pattern or generic intro
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

def gradio_dashboard():
    with gr.Blocks(css="""
.html-report h1, .html-report h2, .html-report h3 {
    color: #22223b;
    font-weight: bold;
    font-family: 'Times New Roman', Times, serif;
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
    margin-left: 2.2em;
    margin-bottom: 1.2em;
    font-size: 0.97em;
    font-family: 'Times New Roman', Times, serif;
}
.html-report li {
    color: #22223b;
    font-size: 0.97em;
    margin-bottom: 0.25em;
    font-family: 'Times New Roman', Times, serif;
    padding-left: 0.2em;
}
.html-report p {
    font-family: 'Times New Roman', Times, serif;
    font-size: 1.01em;
    margin-bottom: 0.7em;
    color: #22223b;
}
.html-report table, .html-report th, .html-report td {
    border: 1.5px solid #22223b !important;
    border-collapse: collapse !important;
    padding: 7px 8px !important;
    font-size: 0.98em !important;
    background: #fff !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    max-width: 120px !important;
    font-family: 'Times New Roman', Times, serif;
}
.html-report th, .html-report td {
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    max-width: 120px !important;
}
.html-report table {
    display: block;
    overflow-x: auto;
    width: 100% !important;
    max-width: 100% !important;
    margin-left: auto;
    margin-right: auto;
}
.html-report th {
    background: #fff !important;
    font-weight: bold !important;
    color: #22223b !important;
}
.html-report tr:nth-child(even) {
    background: #f3f4f6 !important;
}
.html-report tr:hover {
    background: #e5e5e5 !important;
}
.html-report img {
    border: 1.5px solid #22223b;
    border-radius: 10px;
    margin: 18px auto;
    display: block;
    max-width: 350px;
    max-height: 220px;
    object-fit: contain;
    background: #fff;
}
.html-report code {
    background-color: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    color: #22223b;
}
.html-report pre {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 15px;
    overflow-x: auto;
    margin: 15px 0;
}
.html-report pre code {
    background: none;
    padding: 0;
    color: #22223b;
}
""") as demo:
        gr.HTML('<h1>💡 Agentic BA Dashboard</h1>')
        gr.Markdown("Welcome to your AI-powered business analysis system!")
        
        with gr.Row():
            with gr.Column(scale=3):
                business_problem = gr.Textbox(
                    label="Business Problem / Objective", 
                    value="", 
                    lines=8, 
                    placeholder="Paste your business case or objective here..."
                )
        
        with gr.Row():
            run_btn = gr.Button("🚀 Generate Report", variant="primary", size="lg")
            download_btn = gr.Button("📄 Download PDF", variant="secondary", size="lg", visible=False)
        
        status = gr.Textbox(label="Status", value="Ready to generate report...", interactive=False)
        report_output = gr.HTML(label="Generated Report")
        pdf_download = gr.File(label="Download PDF", file_types=[".pdf"], visible=False)
        
        # Store the current report data for PDF generation
        current_report_data = gr.State({"html": "", "business_problem": ""})
        
        def run_and_status(bp):
            try:
                status_msg = "Generating report... (this may take a moment)"
                report, images = generate_report_and_images(bp)
                # Replace each ```mermaid ... ``` block with the corresponding PNG image as base64
                for idx, img_path in enumerate(images, 1):
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as img_file:
                            b64 = base64.b64encode(img_file.read()).decode("utf-8")
                        img_tag = f'<img src="data:image/png;base64,{b64}" style="max-width:100%; margin: 20px 0;" />'
                        report = re.sub(r"```mermaid[\s\S]*?```", img_tag, report, count=1)
                import markdown
                html_report = markdown.markdown(report, extensions=['tables', 'fenced_code'])
                html_report = f'<div class="html-report">{html_report}</div>'
                html_report = remove_emojis(html_report)
                html_report = remove_llm_intro_paragraph(html_report)
                final_status = "Report generated successfully!" if "Error" not in report else "Generation failed - see error message above"
                
                # Store data for PDF generation
                report_data = {"html": html_report, "business_problem": bp}
                
                return html_report, final_status, report_data, gr.update(visible=True), gr.update(visible=True)
            except Exception as e:
                return f"Error: {str(e)}", "Generation failed", {"html": "", "business_problem": ""}, gr.update(visible=False), gr.update(visible=False)
        
        def download_pdf(report_data):
            try:
                if not report_data or not report_data.get("html"):
                    return None, "No report available for download"
                # Remove sticker images and emojis
                html_clean = remove_sticker_images(report_data["html"])
                html_clean = remove_emojis(html_clean)
                html_clean = remove_llm_intro_paragraph(html_clean)
                html_final = wrap_html_with_css(html_clean)
                # Use Playwright to generate PDF
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"business_analysis_report_{timestamp}.pdf"
                temp_file_path = os.path.join(OUTPUT_DIR, filename)
                html_to_pdf_with_playwright(html_final, temp_file_path)
                if os.path.exists(temp_file_path):
                    return temp_file_path, "PDF generated successfully!"
                else:
                    return None, "Failed to generate PDF"
            except Exception as e:
                return None, f"PDF generation error: {str(e)}"
        
        run_btn.click(
            run_and_status, 
            inputs=[business_problem], 
            outputs=[report_output, status, current_report_data, download_btn, pdf_download]
        )
        
        download_btn.click(
            download_pdf,
            inputs=[current_report_data],
            outputs=[pdf_download, status]
        )
    
    return demo

# Create the Gradio app instance for Hugging Face Spaces
demo = gradio_dashboard()

if __name__ == "__main__":
    demo.launch(server_port=7861, share=True)
