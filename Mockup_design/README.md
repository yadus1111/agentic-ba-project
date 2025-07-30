# BRD to HTML Mockup Generator (brd-webapp)

## 🚀 Overview

This web application converts Business Requirements Documents (BRDs) into interactive HTML mockups using AI. It leverages Google Gemini AI to generate a UI schema from your BRD, then renders a visual mockup in your browser.

## 📦 Features

- Paste your BRD and instantly generate a UI mockup
- Uses Google Gemini AI for schema generation
- Renders mockups as HTML for quick visualization
- Simple, clean web interface

## 🛠️ Setup & Installation

1. **Clone the repository** and navigate to the `brd-webapp` directory:
   ```bash
   cd mockup_design/brd-webapp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment:**
   - Create a `.env` file in this directory with your Google Gemini API key:
     ```env
     GEMINI_API_KEY=your_google_gemini_api_key
     ```

4. **Run the app:**
   ```bash
   python app.py
   ```
   The app will be available at [http://localhost:5000](http://localhost:5000).

## 📝 Usage

1. Open the web app in your browser.
2. Paste your BRD text into the textarea.
3. Click **Generate Mockup**.
4. View the generated UI mockup instantly below.

## 📁 File Structure

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `templates/index.html` - Web frontend template
- `static/` - (Optional) Static assets

## 🧩 Dependencies

- Flask
- flask-cors
- google-genai
- python-dotenv

Install all dependencies with `pip install -r requirements.txt`.

## ⚙️ How It Works

1. **User submits BRD** via the web form.
2. **Backend sends BRD** to Google Gemini AI, requesting a UI schema in JSON.
3. **Schema is parsed** and converted to HTML elements.
4. **Mockup is rendered** in the browser for instant feedback.

---

*For questions or issues, please contact the project maintainer.* 