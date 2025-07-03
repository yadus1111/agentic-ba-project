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
        // Simple Mermaid rendering function
        function renderMermaid_{diagram_id.replace('-', '_')}() {{
            try {{
                if (typeof mermaid !== 'undefined') {{
                    mermaid.render('mermaid-{diagram_id}', `{escaped_code}`).then(function(result) {{
                        document.getElementById('mermaid-{diagram_id}').innerHTML = result.svg;
                    }}).catch(function(error) {{
                        console.error('Mermaid rendering error:', error);
                        document.getElementById('mermaid-{diagram_id}').innerHTML = 
                            '<div style="color: red; padding: 10px;">Error rendering diagram. Code: <pre>' + 
                            '{mermaid_code.replace("'", "\\'")}' + '</pre></div>';
                    }});
                }} else {{
                    // If Mermaid is not loaded yet, try again in 500ms
                    setTimeout(renderMermaid_{diagram_id.replace('-', '_')}, 500);
                }}
            }} catch (error) {{
                console.error('Mermaid error:', error);
                document.getElementById('mermaid-{diagram_id}').innerHTML = 
                    '<div style="color: red; padding: 10px;">Error: ' + error.message + '</div>';
            }}
        }}
        
        // Start rendering when DOM is ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', renderMermaid_{diagram_id.replace('-', '_')});
        }} else {{
            renderMermaid_{diagram_id.replace('-', '_')}();
        }}
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
        // Initialize Mermaid with better error handling
        try {
            mermaid.initialize({
                startOnLoad: false,  // Don't auto-start, we'll call it manually
                theme: 'default',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                },
                securityLevel: 'loose',
                logLevel: 1  // Enable some logging for debugging
            });
            console.log('Mermaid initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Mermaid:', error);
        }
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