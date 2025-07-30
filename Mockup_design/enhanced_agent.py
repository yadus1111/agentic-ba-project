#!/usr/bin/env python3
"""
Enhanced BRD Agent - Nepal Fintech Business Analyst Tool
=======================================================

This agent can:
1. Read PDF documents and extract text
2. Generate UI schemas from BRD content
3. Convert schemas to HTML mockups with Nepal-specific context
4. Use Nepali Rupees (Rs.) and local business practices
"""

import json
import re
import os
import sys
from datetime import datetime
from pathlib import Path
import pdfplumber
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnhancedBRDAgent:
    def __init__(self):
        # Check for Gemini AI availability
        try:
            from google import genai
            self.client = genai.Client()
            print("✓ Gemini AI client initialized")
        except ImportError:
            print("Google Generative AI not available. Install with: pip install google-generativeai")
            self.client = None
        except Exception as e:
            print(f"✗ Failed to initialize Gemini client: {e}")
            self.client = None
        
        # PDF generation removed - focus on HTML mockups only
        self.pdf_generator = None
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF file"""
        try:
            print(f"Reading PDF: {pdf_path}")
            with pdfplumber.open(pdf_path) as pdf:
                text_content = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {i+1} ---\n{page_text}")
                    else:
                        text_content.append(f"--- Page {i+1} ---\n[No text content]")
                
                full_text = "\n\n".join(text_content)
                print(f"✓ Extracted {len(full_text)} characters from {len(pdf.pages)} pages")
                return full_text
        except Exception as e:
            print(f"✗ Error reading PDF: {e}")
            return None
    
    def analyze_brd_content(self, brd_text):
        """Analyze BRD content to determine the type of application"""
        if not self.client:
            print("✗ Gemini client not available")
            return "generic"
        
        try:
            prompt = f"""
            Analyze the following BRD (Business Requirements Document) and determine the primary type of application it describes.
            
            Return only one of these categories:
            - "crm" (Customer Relationship Management)
            - "banking" (Digital Banking/Financial Services)
            - "insurance" (Insurance Management)
            - "ecommerce" (E-commerce/Online Shopping)
            - "healthcare" (Healthcare Management)
            - "education" (Learning Management System)
            - "hr" (Human Resources Management)
            - "inventory" (Inventory Management)
            - "project" (Project Management)
            - "generic" (Generic Business Application)
            
            BRD Content:
            {brd_text[:2000]}...
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            app_type = response.text.strip().lower()
            print(f"✓ Detected application type: {app_type}")
            return app_type
        except Exception as e:
            print(f"✗ Error analyzing BRD content: {e}")
            return "generic"
    
    def generate_ui_schema(self, brd_text, app_type="generic"):
        """Generate UI schema from BRD text"""
        if not self.client:
            print("✗ Gemini client not available")
            return None
        
        try:
            # Enhanced prompt based on application type
            type_specific_instructions = {
                "crm": "Focus on customer profiles, contact management, sales opportunities, and customer service features.",
                "banking": "Include account management, transactions, payments, and financial services features.",
                "insurance": "Include policy management, claims processing, and premium calculations.",
                "ecommerce": "Include product catalogs, shopping carts, order management, and payment processing.",
                "healthcare": "Include patient records, appointment scheduling, and medical information management.",
                "education": "Include course management, student records, and learning materials.",
                "hr": "Include employee records, payroll, and performance management.",
                "inventory": "Include stock management, product tracking, and warehouse operations.",
                "project": "Include task management, timelines, and team collaboration.",
                "generic": "Create a general business application interface."
            }
            
            specific_instruction = type_specific_instructions.get(app_type, type_specific_instructions["generic"])
            
            prompt = f"""
            You are an expert UI designer. Convert the following BRD into a JSON schema for a modern web application mockup.
            
            Application Type: {app_type.upper()}
            Focus Areas: {specific_instruction}
            
            IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON.
            
            Requirements:
            - Use an array of objects, each with type (frame, text, rectangle, button, etc.), x, y, width, height, and content/name as appropriate
            - For each text/button/icon, add a 'parent' property with the name of the rectangle/card/container it belongs to, or null if it is a top-level element
            - Group related UI elements (e.g., all fields in a card) under the same parent
            - Use generic field names and labels for all text and content, such as 'First Name', 'Last Name', 'Account Balance', 'Address Field', 'Date of Birth', etc. Do not use real or business-specific data
            - Include clickable buttons for main actions
            - Create a modern, responsive layout
            - Only return the JSON array, no explanation

            BRD:
            {brd_text}
            """
            
            print("Generating UI schema...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # Try to parse the response directly first
            try:
                schema = json.loads(response.text.strip())
                print(f"✓ Generated UI schema with {len(schema)} elements")
                return schema
            except json.JSONDecodeError:
                # Try to extract JSON using regex
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    try:
                        schema = json.loads(match.group(0))
                        print(f"✓ Extracted UI schema with {len(schema)} elements")
                        return schema
                    except json.JSONDecodeError:
                        pass
                
                print("✗ Could not parse AI-generated JSON, using fallback schema")
                return self._generate_fallback_schema(app_type)
        except Exception as e:
            print(f"✗ Error generating UI schema: {e}")
            print("Using fallback schema...")
            return self._generate_fallback_schema(app_type)
    
    def _generate_fallback_schema(self, app_type):
        """Generate a fallback schema when AI generation fails"""
        print(f"Generating fallback schema for {app_type} application...")
        
        if app_type == "crm":
            return [
                {"type": "frame", "name": "CRM Dashboard", "x": 0, "y": 0, "width": 1440, "height": 900},
                {"type": "rectangle", "name": "Header", "x": 0, "y": 0, "width": 1440, "height": 60, "parent": "CRM Dashboard"},
                {"type": "text", "name": "App Title", "x": 20, "y": 20, "width": 200, "height": 20, "content": "360 Degree CRM", "parent": "Header"},
                {"type": "button", "name": "Search", "x": 300, "y": 15, "width": 80, "height": 30, "content": "Search", "parent": "Header"},
                {"type": "rectangle", "name": "Customer Card", "x": 20, "y": 80, "width": 400, "height": 200, "parent": "CRM Dashboard"},
                {"type": "text", "name": "Customer Name", "x": 30, "y": 90, "width": 380, "height": 20, "content": "Customer Name", "parent": "Customer Card"},
                {"type": "text", "name": "Customer ID", "x": 30, "y": 120, "width": 380, "height": 20, "content": "Customer ID", "parent": "Customer Card"},
                {"type": "button", "name": "Edit Customer", "x": 30, "y": 150, "width": 120, "height": 30, "content": "Edit Customer", "parent": "Customer Card"},
                {"type": "button", "name": "View History", "x": 160, "y": 150, "width": 120, "height": 30, "content": "View History", "parent": "Customer Card"}
            ]
        elif app_type == "banking":
            return [
                {"type": "frame", "name": "Banking Dashboard", "x": 0, "y": 0, "width": 1440, "height": 900},
                {"type": "rectangle", "name": "Header", "x": 0, "y": 0, "width": 1440, "height": 60, "parent": "Banking Dashboard"},
                {"type": "text", "name": "App Title", "x": 20, "y": 20, "width": 200, "height": 20, "content": "Digital Banking", "parent": "Header"},
                {"type": "button", "name": "Transfer", "x": 300, "y": 15, "width": 80, "height": 30, "content": "Transfer", "parent": "Header"},
                {"type": "rectangle", "name": "Account Card", "x": 20, "y": 80, "width": 400, "height": 200, "parent": "Banking Dashboard"},
                {"type": "text", "name": "Account Number", "x": 30, "y": 90, "width": 380, "height": 20, "content": "Account Number", "parent": "Account Card"},
                {"type": "text", "name": "Balance", "x": 30, "y": 120, "width": 380, "height": 20, "content": "Balance", "parent": "Account Card"},
                {"type": "button", "name": "Pay Bills", "x": 30, "y": 150, "width": 120, "height": 30, "content": "Pay Bills", "parent": "Account Card"},
                {"type": "button", "name": "Apply for Loan", "x": 160, "y": 150, "width": 120, "height": 30, "content": "Apply for Loan", "parent": "Account Card"}
            ]
        else:
            return [
                {"type": "frame", "name": "Application Dashboard", "x": 0, "y": 0, "width": 1440, "height": 900},
                {"type": "rectangle", "name": "Header", "x": 0, "y": 0, "width": 1440, "height": 60, "parent": "Application Dashboard"},
                {"type": "text", "name": "App Title", "x": 20, "y": 20, "width": 200, "height": 20, "content": "Business Application", "parent": "Header"},
                {"type": "button", "name": "Search", "x": 300, "y": 15, "width": 80, "height": 30, "content": "Search", "parent": "Header"},
                {"type": "rectangle", "name": "Main Card", "x": 20, "y": 80, "width": 400, "height": 200, "parent": "Application Dashboard"},
                {"type": "text", "name": "Title", "x": 30, "y": 90, "width": 380, "height": 20, "content": "Main Section", "parent": "Main Card"},
                {"type": "button", "name": "Action 1", "x": 30, "y": 150, "width": 120, "height": 30, "content": "Action 1", "parent": "Main Card"},
                {"type": "button", "name": "Action 2", "x": 160, "y": 150, "width": 120, "height": 30, "content": "Action 2", "parent": "Main Card"}
            ]

    def convert_schema_to_html(self, schema, app_type="generic", brd_text=None):
        """Convert UI schema to completely dynamic HTML mockup from BRD"""
        if not schema:
            print("✗ No schema provided")
            return None
        
        try:
            # Generate completely dynamic HTML based on BRD analysis
            html_content = self._generate_dynamic_html_from_brd(app_type, brd_text)
            
            print(f"✓ Generated completely dynamic HTML mockup for {app_type} application")
            return html_content
        except Exception as e:
            print(f"✗ Error converting schema to HTML: {e}")
            return None

    def _generate_dynamic_html_from_brd(self, app_type, brd_text=None):
        """Generate completely dynamic HTML from BRD analysis"""
        if not self.client:
            return self._get_fallback_html(app_type)
        
        try:
            brd_section = f"\n\nBRD Content (for reference):\n{brd_text[:4000]}\n" if brd_text else ""
            prompt = f"""
            Based on the following BRD content, generate a complete HTML mockup for a BUSINESS ANALYST DASHBOARD specifically designed for BUSINESS ANALYSTS working in FINTECH companies.
            {brd_section}
            BUSINESS ANALYST REQUIREMENTS:
            1. Create a BUSINESS ANALYST DASHBOARD (not customer-facing interface)
            2. Show CUSTOMER ANALYTICS and INSIGHTS from analyst perspective
            3. Include CUSTOMER PROFILES with detailed information
            4. Display CUSTOMER SEGMENTATION and ANALYSIS
            5. Show BUSINESS METRICS and KPIs
            6. Include CUSTOMER BEHAVIOR PATTERNS
            7. Display FINANCIAL ANALYSIS and TRENDS
            8. Show CUSTOMER INTERACTION HISTORY
            9. Include RISK ASSESSMENT and COMPLIANCE data
            10. Display CUSTOMER SATISFACTION metrics
            
            CURRENCY AND CONTEXT REQUIREMENTS:
            1. Use RUPEES (Rs.) instead of dollars - format as "Rs. 1,25,000" (with commas at thousands)
            2. Include BANKING CONTEXT: Central Bank regulations, local banks, etc.
            3. Use INTERNATIONAL BUSINESS TERMINOLOGY: "Account", "Transaction", "Banking Service"
            4. Use NEPALI NAMES: Common names like Sita, Ram, Gita, Hari, etc.
            5. Include NEPALI LOCATIONS: Kathmandu, Pokhara, Biratnagar, Lalitpur, etc.
            6. Use NEPALI CURRENCY FORMAT: Rs. 1,00,000 (not $100,000)
            7. Include INTERNATIONAL BUSINESS PRACTICES: Standard business hours, calendar references
            
            DASHBOARD FEATURES:
            1. Customer Overview Cards with key metrics
            2. Customer Segmentation Analysis
            3. Financial Performance Charts
            4. Customer Behavior Analytics
            5. Risk Assessment Dashboard
            6. Compliance Monitoring
            7. Customer Interaction Timeline
            8. Business Intelligence Reports
            9. Data Export and Filtering
            10. Real-time Analytics
            
            TECHNICAL REQUIREMENTS:
            1. Generate the ENTIRE HTML structure from scratch - no predefined templates
            2. Include modern CSS styling with gradients, shadows, and responsive design
            3. Create interactive JavaScript for buttons, search, and data filtering
            4. Use content that reflects the actual BRD requirements
            5. Include charts, graphs, and data visualization elements
            6. Make it professional and modern looking
            7. Include clickable buttons with hover effects
            8. Use a color scheme appropriate for business analytics
            9. Use ONLY ENGLISH LANGUAGE throughout the interface
            
            Return ONLY the complete HTML document. Do not include any explanations or markdown.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            html_content = response.text.strip()
            
            # Clean up the response to ensure it's valid HTML
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            
            print("✓ Generated completely dynamic HTML from BRD")
            return html_content
                
        except Exception as e:
            print(f"✗ Error generating dynamic HTML: {e}")
            return self._get_fallback_html(app_type)
    
    def _get_fallback_html(self, app_type):
        """Get fallback HTML when AI generation fails"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nepal Fintech {app_type.upper()} Application</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1440px; margin: 0 auto; background: white; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .app-title {{ font-size: 24px; font-weight: bold; }}
        .search-section {{ display: flex; align-items: center; gap: 10px; flex: 1; max-width: 600px; margin: 0 20px; }}
        .search-input {{ flex: 1; padding: 10px 15px; border: none; border-radius: 25px; font-size: 14px; background: rgba(255,255,255,0.9); color: #333; }}
        .search-btn {{ padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: 500; transition: all 0.3s ease; }}
        .search-btn:hover {{ background: #45a049; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
        .main-content {{ padding: 20px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; min-height: calc(100vh - 80px); }}
        .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; margin-bottom: 20px; }}
        .card-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: 500; transition: all 0.3s ease; text-decoration: none; display: inline-block; text-align: center; margin: 5px; }}
        .btn-primary {{ background: #4CAF50; color: white; }}
        .btn-success {{ background: #27ae60; color: white; }}
        .btn-warning {{ background: #f39c12; color: white; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
        .data-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
        .data-label {{ font-weight: 600; color: #555; min-width: 120px; }}
        .data-value {{ color: #333; text-align: right; flex: 1; }}
        .btn-group {{ display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }}
        @media (max-width: 1200px) {{ .main-content {{ grid-template-columns: 1fr; }} }}
        .card {{ transition: transform 0.3s ease, box-shadow 0.3s ease; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="app-title">Business Analyst Dashboard - {app_type.upper()} Analytics</div>
            <div class="search-section">
                <input type="text" class="search-input" placeholder="Search...">
                <button class="search-btn" onclick="performSearch()">Search</button>
            </div>
            <div class="user-info">
                <div class="user-name">Sita Sharma</div>
                <div class="user-role">Business Analyst (Nepal)</div>
            </div>
        </header>
        <main class="main-content">
            <div class="left-column">
                <div class="card">
                    <h3 class="card-title">Overview (Kathmandu)</h3>
                    <div class="data-row">
                        <span class="data-label">Total Customers:</span>
                        <span class="data-value">1,250</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">Active in Pokhara:</span>
                        <span class="data-value">1,180</span>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="alert('Action 1')">Action 1</button>
                        <button class="btn btn-success" onclick="alert('Action 2')">Action 2</button>
                    </div>
                </div>
            </div>
            <div class="middle-column">
                <div class="card">
                    <h3 class="card-title">Recent Activity (Biratnagar)</h3>
                    <div class="data-row">New account opened - Dec 15, 2024</div>
                    <div class="data-row">Loan approved - Dec 14, 2024</div>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="alert('View All')">View All</button>
                    </div>
                </div>
            </div>
            <div class="right-column">
                <div class="card">
                    <h3 class="card-title">Quick Actions (Lalitpur)</h3>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="alert('Create New')">Create New</button>
                        <button class="btn btn-success" onclick="alert('Generate Report')">Generate Report</button>
                        <button class="btn btn-warning" onclick="alert('Settings')">Settings</button>
                    </div>
                </div>
            </div>
        </main>
    </div>
    <script>
        function performSearch() {{
            const searchTerm = document.querySelector('.search-input').value;
            if (searchTerm.trim()) {{
                alert(`Searching for: ${{searchTerm}}`);
            }} else {{
                alert('Please enter a search term');
            }}
        }}
        
        document.querySelector('.search-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                performSearch();
            }}
        }});
        
        document.querySelectorAll('.btn').forEach(button => {{
            button.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-2px)';
            }});
            button.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0)';
            }});
            button.addEventListener('click', function() {{
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    this.style.transform = 'scale(1)';
                }}, 150);
            }});
        }});
    </script>
</body>
</html>"""
    
    def save_outputs(self, schema, html_content, app_type, timestamp):
        """Save all outputs to files"""
        # Create output directories
        output_dirs = ['schemas', 'html_mockups', 'pdf_mockups']
        for dir_name in output_dirs:
            os.makedirs(dir_name, exist_ok=True)
        
        # Save schema
        schema_filename = f"schemas/{app_type}_schema_{timestamp}.json"
        with open(schema_filename, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        print(f"✓ Schema saved: {schema_filename}")
        
        # Save HTML
        html_filename = f"html_mockups/{app_type}_mockup_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML mockup saved: {html_filename}")
        
        return {
            'schema': schema_filename,
            'html': html_filename
        }
    
    def process_pdf_pipeline(self, pdf_path):
        """Complete pipeline: PDF → Schema → HTML → Save"""
        print("=" * 60)
        print("Enhanced BRD Agent - Complete Pipeline")
        print("=" * 60)
        
        # Step 1: Extract text from PDF
        print("\n📄 Step 1: Extracting text from PDF...")
        brd_text = self.extract_text_from_pdf(pdf_path)
        if not brd_text:
            print("✗ Failed to extract text from PDF")
            return None
        
        # Step 2: Analyze BRD content
        print("\n🔍 Step 2: Analyzing BRD content...")
        app_type = self.analyze_brd_content(brd_text)
        
        # Step 3: Generate UI schema
        print("\n🎨 Step 3: Generating UI schema...")
        schema = self.generate_ui_schema(brd_text, app_type)
        if not schema:
            print("✗ Failed to generate UI schema")
            return None
        
        # Step 4: Convert to HTML
        print("\n🌐 Step 4: Converting to HTML mockup...")
        html_content = self.convert_schema_to_html(schema, app_type, brd_text)
        if not html_content:
            print("✗ Failed to convert schema to HTML")
            return None
        
        # Step 5: Save outputs
        print("\n💾 Step 5: Saving outputs...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs = self.save_outputs(schema, html_content, app_type, timestamp)
        
        print("\n" + "=" * 60)
        print("✅ Pipeline completed successfully!")
        print("=" * 60)
        print(f"Application Type: {app_type.upper()}")
        print(f"Schema: {outputs['schema']}")
        print(f"HTML Mockup: {outputs['html']}")
        
        return outputs

def main():
    """Main function with interactive menu"""
    agent = EnhancedBRDAgent()
    
    if not hasattr(agent, 'client') or agent.client is None:
        print("✗ Gemini AI not available. Please install google-generativeai")
        return
    
    if not hasattr(agent, 'mockup_generator') or agent.mockup_generator is None:
        print("✗ Mockup generators not available")
        return
    
    print("\nEnhanced BRD Agent - PDF to HTML Pipeline")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Process PDF file")
        print("2. Process text input")
        print("3. Generate sample mockups")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            pdf_path = input("Enter path to PDF file: ").strip()
            if os.path.exists(pdf_path):
                agent.process_pdf_pipeline(pdf_path)
            else:
                print("✗ File not found")
        
        elif choice == "2":
            print("Paste your BRD text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            
            brd_text = "\n".join(lines[:-1])  # Remove the last empty line
            if brd_text.strip():
                app_type = agent.analyze_brd_content(brd_text)
                schema = agent.generate_ui_schema(brd_text, app_type)
                if schema:
                    html_content = agent.convert_schema_to_html(schema, app_type, brd_text)
                    if html_content:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        agent.save_outputs(schema, html_content, app_type, timestamp)
            else:
                print("✗ No text provided")
        
        elif choice == "3":
            print("Generating sample mockups...")
            if agent.mockup_generator:
                agent.mockup_generator.generate_all_mockups()
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 