# Agentic Business Analysis Dashboard

An AI-powered dashboard for generating comprehensive business analysis reports using specialized AI agents.

## 🚀 Features

- 🤖 **Multi-Agent AI System**: 7 specialized AI agents working together
- 📊 **Visual Diagrams**: Automatic Mermaid diagram generation
- 📋 **Complete Reports**: BRD, FRS, use cases, data mapping, and KPIs
- 🎨 **Modern UI**: Beautiful Gradio interface with animations
- 🔄 **Error Resilience**: Automatic retries and fallback mechanisms
- 🌐 **Domain Agnostic**: Works for any business domain (not just banking)

## 🎯 How to Use

1. Enter your business problem in the text area
2. Click "Generate Report" 
3. Get a comprehensive business analysis with:
   - Stakeholder maps
   - Process flows
   - Business requirements
   - Use case diagrams
   - Data mapping sheets
   - KPIs and metrics

## 🛠️ Technical Stack

- **Frontend**: Gradio
- **AI Model**: Google Gemini 2.5 Flash
- **Diagrams**: Mermaid.js
- **Architecture**: Multi-Agent System
- **Deployment**: Hugging Face Spaces

## ⚙️ Setup Required

### For Hugging Face Spaces:

1. **Add your Gemini API key as a secret:**
   - Go to your Space Settings → Secrets
   - Add: `GEMINI_API_KEY` = your_api_key_here

2. **Get your Gemini API key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy and paste it as the secret above

## 📁 File Structure

```
BA-Agentic-AI/
├── app.py              # Main entry point for HF Spaces
├── ba_dashboard.py     # Core dashboard logic
├── agents.py           # AI agent definitions
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── deploy_to_hf.py     # Deployment helper script
└── README_HF.md        # This file
```

## 🔧 Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `GEMINI_API_KEY=your_key_here`
4. Run: `python ba_dashboard.py`

## 🌟 Key Improvements

- **Generic Business Analysis**: No longer limited to banking/loan scenarios
- **Dynamic Content Generation**: Responds to your specific business problem
- **Flexible Stakeholder Mapping**: Identifies relevant stakeholders for any domain
- **Adaptive Process Flows**: Creates process flows specific to your business case

## 🎨 UI Features

- Beautiful gradient animations
- Responsive design
- Modern card-based layout
- Interactive elements with hover effects
- Professional typography and spacing

## 🔒 Privacy & Security

- API keys are stored as environment variables
- No data is stored permanently
- All processing happens in real-time
- Secure API communication with Google Gemini

## 🐛 Troubleshooting

**API Overload Errors:**
- The system automatically retries up to 3 times
- Wait a few minutes and try again
- Check your API key is valid

**Diagram Generation Issues:**
- Fallback templates are provided
- Simple Mermaid syntax is enforced
- Error messages are displayed for debugging

## 📞 Support

If you encounter issues:
1. Check your API key is correctly set
2. Ensure you have sufficient API quota
3. Try refreshing the page
4. Check the status messages for error details

---

*Built with ❤️ using Agentic AI principles*

**Live Demo:** [Your HF Space URL will be here] 