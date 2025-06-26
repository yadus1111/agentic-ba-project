import os
from agents import AGENTS, client
from config import MODEL_NAME

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Comprehensive prompts for each deliverable
REPORT_PROMPTS = {
    "01_Stakeholder_Map.md": """
You are a Process Modeler. Create a stakeholder map in Mermaid format for the loan personalization project.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Create a clear stakeholder map showing:
- Customer (end user)
- Mobile Banking App
- IT Team (manages the app)
- Loan Module (features)
- Product Owner (owns the project)
- Marketing Team
- Compliance Team
- Data Team
- Recommendation Engine
- Customer Data (data sources)

Use Mermaid graph TD format with clear relationships like "Uses", "Managed by", "Features", "Owned by", "Provides", "Uses".

Output ONLY the Mermaid diagram code, no additional text.
""",

    "02_Process_Flow.md": """
You are a Process Modeler. Create a process flow diagram in Mermaid format for the new loan uptake journey.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Create a sequence diagram showing the complete loan recommendation and application process:
- Customer logs into mobile app
- Mobile app requests personalized loan offers
- Recommendation engine fetches customer data
- Data sources return customer profile
- Recommendation engine analyzes data and generates offers
- Mobile app displays personalized offers
- Customer clicks on loan offer
- Loan module shows application form
- Customer submits application
- Loan module provides confirmation

Use Mermaid sequenceDiagram format with clear participant names and flow steps.

Output ONLY the Mermaid diagram code, no additional text.
""",

    "03_Business_Requirement_Document.md": """
You are a Business Analyst. Write a comprehensive Business Requirement Document (BRD) for the loan personalization project.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Structure your response exactly as follows:

**Business Problem:**
[Describe the current low loan uptake issue]

**Objective:**
[State the goal of increasing loan conversions through personalization]

**Scope:**
**In:** [List what's included in scope]
**Out:** [List what's excluded from scope]

**High-Level Requirements:**
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Make it concise, clear, and actionable.
""",

    "04_Functional_Requirement_Specification.md": """
You are a Business Analyst. Write a Functional Requirement Specification (FRS) including Non-Functional Requirements.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Structure your response exactly as follows:

**Functional Requirements:**
- [Requirement 1: System must analyze customer data...]
- [Requirement 2: Offers must be displayed...]
- [Requirement 3: System must log user interactions...]

**Non-Functional Requirements:**
- [NFR 1: Data privacy and security...]
- [NFR 2: Real-time processing...]
- [NFR 3: High availability...]

Make it specific, measurable, and focused on the loan personalization system.
""",

    "05_Use_Cases_and_Scenarios.md": """
You are a Use Case Analyst. Develop detailed use case scenarios for the three specified cases.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Structure your response exactly as follows:

**Use Case 1:**
Recommending loan offers based on income bracket and transaction behavior.
**Actors:** [List actors]
**Preconditions:** [List preconditions]
**Main Flow:** [Describe main flow]
**Exceptions:** [List exceptions]

**Use Case 2:**
Targeting customers with education expenses for educational loan promotions.
**Actors:** [List actors]
**Main Flow:** [Describe main flow]

**Use Case 3:**
Pre-approval and alerting customers with consistent salary inflow for personal loans.
**Actors:** [List actors]
**Main Flow:** [Describe main flow]

Make each use case specific and actionable.
""",

    "06_Data_Mapping_Sheet.md": """
You are a Data Analyst. Create a comprehensive data mapping sheet for the loan personalization project.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Create a Markdown table with the following columns:
| Feature | Data Point Required | Source System | Freshness |

Include at least these features:
- Personal Loan Pre-approval
- Education Loan Recommendation
- Offer Personalization

Make the data points specific and actionable.
""",

    "07_Functional_Scope_Summary.md": """
You are a Business Analyst. Write a functional scope summary for the loan personalization project.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Structure your response exactly as follows:

**In Scope:**
- [Scope item 1]
- [Scope item 2]
- [Scope item 3]

**Out of Scope:**
- [Out of scope item 1]
- [Out of scope item 2]

Be clear and specific about what is and isn't included.
""",

    "08_Suggested_KPIs.md": """
You are a KPI Analyst. Suggest comprehensive KPIs for the loan personalization project.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

List specific, measurable KPIs such as:
- Increase in loan applications via mobile app by X% in Y months
- Offer click-through rate
- Conversion rate from offer to application
- Engagement uplift (interactions with loan products)

Make them specific, measurable, and relevant to the business objectives.
""",

    "README.md": """
You are a Technical Writer. Write a README explaining the generated files.

Business Context: Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking

Write a brief README explaining that this directory contains business analysis deliverables generated for the project: "Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking"

Keep it concise and professional.
"""
}

def generate_comprehensive_report():
    """Generate the complete business analysis report"""
    print("Generating comprehensive business analysis report...")
    
    for filename, prompt in REPORT_PROMPTS.items():
        print(f"Generating {filename}...")
        
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            
            content = response.text if response.text else "Content generation failed"
            
            # Save the file
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✓ Saved: {filename}")
            
        except Exception as e:
            print(f"✗ Error generating {filename}: {str(e)}")
            # Save error message
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Error generating content: {str(e)}")
    
    print("\nReport generation complete!")
    print(f"All files saved in: {OUTPUT_DIR}/")

if __name__ == "__main__":
    generate_comprehensive_report() 