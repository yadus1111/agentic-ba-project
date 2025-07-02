#!/usr/bin/env python3
"""
FastAPI server for BA Agentic AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import ba_dashboard
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ba_dashboard import generate_report_and_images

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BA Agentic AI API",
    description="Business Analysis Agentic AI API for generating comprehensive business analysis reports",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BusinessProblemRequest(BaseModel):
    business_problem: str

class BusinessProblemResponse(BaseModel):
    report: str
    images: list
    success: bool
    message: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BA Agentic AI API",
        "version": "1.0.0",
        "endpoints": {
            "generate_report": "/generate-report",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "model": "gemini-1.5-flash"
    }

@app.post("/generate-report", response_model=BusinessProblemResponse)
async def generate_report(request: BusinessProblemRequest):
    """Generate a business analysis report"""
    try:
        if not request.business_problem or not request.business_problem.strip():
            raise HTTPException(status_code=400, detail="Business problem is required")
        
        # Check if API key is configured
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="GEMINI_API_KEY not configured. Please set it in your .env file"
            )
        
        # Generate report
        report, images = generate_report_and_images(request.business_problem)
        
        return BusinessProblemResponse(
            report=report,
            images=images,
            success=True,
            message="Report generated successfully"
        )
        
    except Exception as e:
        return BusinessProblemResponse(
            report="",
            images=[],
            success=False,
            message=f"Error generating report: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 