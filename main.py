import os
from agents import AGENTS, client
from config import MODEL_NAME

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BUSINESS_PROBLEM = '''
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

def call_agent(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def main():
    print("\n--- Agentic BA Multi-Agent System ---\n")
    print("Generating business analysis deliverables...")
    for filename, agent_prompt in DELIVERABLES:
        print(f"Generating {filename}...")
        full_prompt = f"{BUSINESS_PROBLEM}\n\n{agent_prompt}"
        content = call_agent(full_prompt)
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved: {filename}")
    print("\nAll deliverables generated in the 'output' directory.")

if __name__ == "__main__":
    main() 