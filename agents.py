from config import GEMINI_API_KEY, MODEL_NAME
from google import genai

# Set up Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

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