import re
import time

def create_mermaid_diagram_html(mermaid_code, diagram_id):
    """Create HTML for Mermaid diagram that works on Hugging Face Spaces"""
    # Escape the mermaid code for JavaScript
    escaped_code = mermaid_code.replace('`', '\\`').replace('\n', '\\n')
    
    html = f"""
    <div class="mermaid-container" style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
        <div class="mermaid" id="mermaid-{diagram_id}">
{mermaid_code}
        </div>
    </div>
    <script>
        (function() {{
            // Wait for Mermaid to be available
            function renderMermaid() {{
                if (typeof mermaid !== 'undefined') {{
                    try {{
                        mermaid.render('mermaid-{diagram_id}', `{escaped_code}`).then(function(result) {{
                            document.getElementById('mermaid-{diagram_id}').innerHTML = result.svg;
                        }});
                    }} catch (error) {{
                        console.error('Mermaid rendering error:', error);
                        document.getElementById('mermaid-{diagram_id}').innerHTML = 
                            '<div style="color: red; padding: 10px;">Error rendering diagram. Code: <pre>' + 
                            '{mermaid_code.replace("'", "\\'")}' + '</pre></div>';
                    }}
                }} else {{
                    setTimeout(renderMermaid, 100);
                }}
            }}
            renderMermaid();
        }})();
    </script>
    """
    return html

def process_markdown_with_mermaid(markdown_text):
    """Process markdown and replace Mermaid code blocks with HTML diagrams"""
    # Find all Mermaid code blocks
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = list(re.finditer(mermaid_pattern, markdown_text, re.DOTALL))
    
    processed_text = markdown_text
    offset = 0
    
    for i, match in enumerate(matches):
        mermaid_code = match.group(1).strip()
        diagram_id = f"diagram-{int(time.time())}-{i}"
        
        # Create HTML for the diagram
        mermaid_html = create_mermaid_diagram_html(mermaid_code, diagram_id)
        
        start = match.start() + offset
        end = match.end() + offset
        processed_text = processed_text[:start] + mermaid_html + processed_text[end:]
        offset += len(mermaid_html) - (end - start)
    
    return processed_text

def create_mermaid_header():
    """Create the HTML header with Mermaid.js library"""
    return """
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11.5.0/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            },
            securityLevel: 'loose'
        });
    </script>
    <style>
        .mermaid-container {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            overflow-x: auto;
        }
        .mermaid-container svg {
            max-width: 100%;
            height: auto;
        }
        .mermaid-container pre {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 12px;
        }
    </style>
    """ 