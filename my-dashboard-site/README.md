# BA Agentic AI Dashboard - Vercel Integration

This is a Next.js frontend that integrates with the BA-Agentic-AI Python backend to provide a modern web interface for business analysis report generation.

## Features

- 🎯 Modern React/Next.js frontend with TypeScript
- 📊 Interactive Mermaid diagram rendering
- 🤖 AI-powered business analysis report generation
- 📱 Responsive design with Tailwind CSS
- 🔄 Real-time API integration with Python backend

## Project Structure

```
my-dashboard-site/
├── app/
│   ├── components/
│   │   ├── BusinessAnalysisForm.tsx    # Form for business problem input
│   │   ├── ReportViewer.tsx            # Report display with Mermaid diagrams
│   │   └── Mermaid.tsx                 # Mermaid diagram renderer
│   ├── api/
│   │   └── ba-analysis/
│   │       └── route.ts                # API route for backend communication
│   ├── page.tsx                        # Main dashboard page
│   └── globals.css                     # Global styles with Tailwind
├── package.json                        # Dependencies and scripts
├── tailwind.config.js                  # Tailwind CSS configuration
├── vercel.json                         # Vercel deployment configuration
└── README.md                           # This file
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+ (for backend)
- Vercel account (for deployment)

## Local Development Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in the root directory:

```env
# Backend API URL (update this with your deployed backend URL)
BACKEND_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Backend Integration

This frontend integrates with the BA-Agentic-AI Python backend. You have two options:

### Option 1: Local Backend Development

1. Navigate to the `BA-Agentic-AI/api/` directory
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up your environment variables (GEMINI_API_KEY)
4. Run the FastAPI server: `python main.py`
5. The backend will be available at `http://localhost:8000`

### Option 2: Deployed Backend

Deploy the Python backend to a cloud service (Railway, Render, Heroku, etc.) and update the `BACKEND_API_URL` environment variable.

## Vercel Deployment

### 1. Deploy Frontend to Vercel

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard:
   - `BACKEND_API_URL`: Your deployed backend URL

### 2. Deploy Backend

Deploy the Python backend to your preferred platform:

#### Railway Deployment
1. Create a new Railway project
2. Connect your GitHub repository
3. Set the source directory to `BA-Agentic-AI/api/`
4. Add environment variables (GEMINI_API_KEY)
5. Deploy

#### Render Deployment
1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### 3. Update Frontend Configuration

After deploying the backend, update the `BACKEND_API_URL` environment variable in your Vercel dashboard with the deployed backend URL.

## Environment Variables

### Frontend (.env.local)
- `BACKEND_API_URL`: URL of your deployed Python backend

### Backend (set in deployment platform)
- `GEMINI_API_KEY`: Your Google Gemini API key

## API Endpoints

### Backend API (FastAPI)
- `GET /`: Health check
- `GET /health`: Health check
- `POST /generate-report`: Generate business analysis report

### Frontend API (Next.js)
- `POST /api/ba-analysis`: Proxy to backend API

## Usage

1. Open the dashboard in your browser
2. Enter a business problem or objective in the text area
3. Click "Generate Business Analysis Report"
4. View the generated report with interactive Mermaid diagrams
5. Use the "Generate New Report" button to create another report

## Troubleshooting

### Common Issues

1. **Backend Connection Error**: Ensure your backend is running and the `BACKEND_API_URL` is correct
2. **Mermaid Diagrams Not Rendering**: Check browser console for JavaScript errors
3. **API Key Issues**: Verify your Gemini API key is set correctly in the backend

### Development Tips

- Use browser developer tools to debug API calls
- Check Vercel function logs for frontend API issues
- Monitor backend logs for Python errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is licensed under the MIT License.
