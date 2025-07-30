#!/usr/bin/env python3
"""
Direct PDF Processing Script
===========================

This script directly processes the user's PDF file and generates custom mockups
based on the BRD content without requiring interactive input.
"""

import os
from enhanced_agent import EnhancedBRDAgent

def main():
    """Process the user's PDF file directly"""
    print("🚀 Enhanced BRD Agent - Processing Your PDF")
    print("=" * 50)
    
    # Initialize the agent
    agent = EnhancedBRDAgent()
    
    # Check if components are available
    if not hasattr(agent, 'client') or agent.client is None:
        print("✗ Gemini AI not available. Please install google-generativeai")
        return
    
    # Mockup generator is no longer needed since we generate HTML dynamically
    print("✓ Dynamic HTML generation enabled")
    
    # Look for PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("✗ No PDF files found in the current directory")
        print("Please place your BRD PDF file in this directory and run again.")
        return
    
    # Show available PDF files and let user choose
    print("📄 Available PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")
    
    if len(pdf_files) == 1:
        pdf_path = pdf_files[0]
        print(f"📄 Using PDF file: {pdf_path}")
    else:
        try:
            choice = input(f"\nSelect PDF file (1-{len(pdf_files)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(pdf_files):
                pdf_path = pdf_files[choice_idx]
                print(f"📄 Selected PDF file: {pdf_path}")
            else:
                print("❌ Invalid choice. Using first PDF file.")
                pdf_path = pdf_files[0]
        except (ValueError, IndexError):
            print("❌ Invalid input. Using first PDF file.")
            pdf_path = pdf_files[0]
    
    # Process the PDF
    print(f"\n🔄 Processing: {pdf_path}")
    print("=" * 50)
    
    try:
        outputs = agent.process_pdf_pipeline(pdf_path)
        
        if outputs:
            print("\n🎉 Success! Your custom mockups have been generated!")
            print("=" * 50)
            print(f"📁 Schema: {outputs['schema']}")
            print(f"🌐 HTML Mockup: {outputs['html']}")
            
            print("\n✨ You can now open the HTML file in your browser to see your custom mockup!")
        else:
            print("\n❌ Failed to process the PDF. Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Error processing PDF: {e}")
        print("Please check that your PDF file is valid and contains text content.")

if __name__ == "__main__":
    main() 