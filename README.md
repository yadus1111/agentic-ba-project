# Agentic BA - Multi-Agent Business Analysis System

A powerful, AI-driven business analysis platform that uses multiple specialized agents to generate comprehensive business analysis deliverables automatically.

## 🚀 Features

### Multi-Agent Architecture
- **Process Modeler** - Creates stakeholder maps and process flows
- **Business Analyst** - Writes BRDs, FRS, and scope summaries
- **Use Case Specialist** - Develops use case diagrams and scenarios
- **Data Analyst** - Creates data mapping sheets and requirements
- **KPI Specialist** - Suggests metrics and success criteria
- **Technical Writer** - Generates documentation

### Two Interface Options
1. **Multi-Agent GUI** (`ba_multiagent_gui.py`) - Step-by-step generation with progress tracking
2. **BA Dashboard** (`ba_dashboard.py`) - Single-click comprehensive report generation

## 📋 Generated Deliverables

- 📊 **Stakeholder Map** (Mermaid diagrams)
- 🔄 **Process Flow Diagrams** (Visual workflows)
- 📋 **Business Requirement Document (BRD)**
- ⚙️ **Functional Requirement Specification (FRS)**
- 🎯 **Use Cases & Scenarios**
- 📊 **Data Mapping & Requirements**
- 🎯 **Functional Scope Summary**
- 📈 **Suggested KPIs**
- 📖 **Complete Documentation**

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agentic-ba-project.git
   cd agentic-ba-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   - Edit `config.py` and add your Google Gemini API key
   - Or set environment variable: `GEMINI_API_KEY=your_api_key_here`

## 🚀 Usage

### Option 1: Multi-Agent GUI (Recommended)
```bash
python ba_multiagent_gui.py
```
- Access at: `http://127.0.0.1:7860`
- Step-by-step generation with progress tracking
- File management and download capabilities

### Option 2: BA Dashboard
```bash
python ba_dashboard.py
```
- Access at: `http://127.0.0.1:7861`
- Single-click comprehensive report generation
- Visual diagram gallery

### Option 3: Command Line
```bash
python main.py
```
- Generates all deliverables automatically
- Saves files to `output/` directory

## 📁 Project Structure

```
agentic_ba_project/
├── agents.py              # Multi-agent definitions
├── ba_agent_gui.py        # Single agent interface
├── ba_multiagent_gui.py   # Multi-agent GUI
├── ba_dashboard.py        # Dashboard interface
├── config.py              # Configuration settings
├── main.py                # Command line interface
├── report_generator.py    # Report generation utilities
├── requirements.txt       # Python dependencies
├── output/                # Generated deliverables
└── README.md             # This file
```

## 🔧 Configuration

### API Setup
1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to `config.py`:
   ```python
   GEMINI_API_KEY = "your_api_key_here"
   ```

### Model Configuration
The system uses `gemini-2.5-flash` by default. You can change this in `config.py`.

## 🎯 Example Use Case

**Business Problem:** "Improving Loan Product Uptake through Data-Driven Personalization in Mobile Banking"

The system will automatically generate:
- Stakeholder map showing all involved parties
- Process flow of the loan uptake journey
- Complete BRD with business requirements
- FRS with functional and non-functional requirements
- Use cases for key scenarios
- Data mapping and requirements analysis
- Scope definition and KPIs

## 🔄 API Retry Logic

The system includes robust error handling:
- **Automatic retries** for API overload (503 errors)
- **Exponential backoff** with random jitter
- **User-friendly status messages**
- **Graceful degradation** when services are unavailable

## 📊 Mermaid Diagrams

The system generates Mermaid diagrams for:
- **Stakeholder Maps** - Simple flowchart showing relationships
- **Process Flows** - Step-by-step journey visualization

Diagrams are saved as both `.mmd` files and rendered as PNG images (when Mermaid CLI is available).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the web interface
- Powered by [Google Gemini](https://ai.google.dev/) AI models
- Uses [Mermaid](https://mermaid.js.org/) for diagram generation

## 📞 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/yourusername/agentic-ba-project/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

**Made with ❤️ for Business Analysts everywhere** 