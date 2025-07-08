#!/usr/bin/env python3
"""
Test script for PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_pdf_from_html

def test_pdf_generation():
    """Test PDF generation with sample content"""
    
    # Sample HTML content
    sample_html = """
    <div class="html-report">
        <h1>Test Business Analysis Report</h1>
        <h2>Stakeholder Analysis</h2>
        <p>This is a test paragraph for the business analysis report.</p>
        <h3>Key Findings</h3>
        <ul>
            <li>First key finding</li>
            <li>Second key finding</li>
            <li>Third key finding</li>
        </ul>
        <table>
            <tr>
                <th>Stakeholder</th>
                <th>Role</th>
                <th>Impact</th>
            </tr>
            <tr>
                <td>Customer</td>
                <td>End User</td>
                <td>High</td>
            </tr>
            <tr>
                <td>Bank Staff</td>
                <td>Support</td>
                <td>Medium</td>
            </tr>
        </table>
    </div>
    """
    
    business_problem = "Improve loan product uptake in mobile banking through personalized recommendations"
    
    print("Testing PDF generation...")
    
    try:
        pdf_bytes = generate_pdf_from_html(sample_html, business_problem)
        
        if pdf_bytes:
            # Save test PDF
            with open("test_report.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("✅ PDF generation successful! Test file saved as 'test_report.pdf'")
            print(f"📄 PDF size: {len(pdf_bytes)} bytes")
            return True
        else:
            print("❌ PDF generation failed - no bytes returned")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF functionality is working correctly!")
    else:
        print("\n💥 PDF functionality needs attention.") 