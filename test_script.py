#!/usr/bin/env python3
"""
Simple test script to check if the BA Agentic AI setup is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_setup():
    print("=== BA Agentic AI Setup Test ===\n")
    
    # Check if GEMINI_API_KEY is set
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        print("✅ GEMINI_API_KEY is set")
    else:
        print("❌ GEMINI_API_KEY is not set or is the default value")
        print("   Please create a .env file with your API key:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    # Test importing the main module
    try:
        from ba_dashboard import generate_report_and_images
        print("✅ ba_dashboard module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ba_dashboard: {e}")
        return False
    
    # Test basic functionality
    try:
        test_problem = "Create a simple business analysis for a coffee shop"
        print(f"\n🧪 Testing with: '{test_problem}'")
        
        report, images = generate_report_and_images(test_problem)
        
        if report and len(report) > 100:
            print("✅ Report generation successful!")
            print(f"   Report length: {len(report)} characters")
            print(f"   Images generated: {len(images)}")
            
            # Show first 200 characters of report
            print(f"\n📄 Report preview:")
            print("-" * 50)
            print(report[:200] + "..." if len(report) > 200 else report)
            print("-" * 50)
            
            return True
        else:
            print("❌ Report generation failed or returned empty content")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_setup()
    
    if success:
        print("\n🎉 Setup is working! You can now run the API server with:")
        print("   python api/main.py")
        print("\nOr use the web interface by running the Next.js app in the my-dashboard-site folder")
    else:
        print("\n🔧 Please fix the issues above before proceeding") 