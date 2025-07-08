#!/usr/bin/env python3
"""
Simple test script for PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_pdf_from_html

def test_simple_pdf():
    """Test PDF generation with simple content"""
    
    # Simple HTML content
    simple_html = """
    <div class="html-report">
        <h1>Test Report</h1>
        <h2>Section 1</h2>
        <p>This is a test paragraph.</p>
        <h3>Subsection</h3>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <table>
            <tr>
                <th>Name</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Test</td>
                <td>123</td>
            </tr>
        </table>
    </div>
    """
    
    business_problem = "Test business problem for PDF generation"
    
    print("Testing PDF generation...")
    
    try:
        pdf_bytes = generate_pdf_from_html(simple_html, business_problem)
        
        if pdf_bytes:
            # Save test PDF
            with open("test_simple.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("✅ PDF generation successful!")
            print(f"📄 PDF size: {len(pdf_bytes)} bytes")
            print("📁 File saved as 'test_simple.pdf'")
            return True
        else:
            print("❌ PDF generation failed - no bytes returned")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_pdf()
    if success:
        print("\n🎉 PDF functionality is working correctly!")
    else:
        print("\n💥 PDF functionality needs attention.") 