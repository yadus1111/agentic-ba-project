import re
import random

def create_simple_svg_diagram(mermaid_code, diagram_id):
    """Create a simple SVG diagram from Mermaid-like syntax"""
    
    # Parse the flowchart
    lines = mermaid_code.strip().split('\n')
    nodes = {}
    connections = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('flowchart'):
            continue
            
        # Parse node definitions: A[Label]
        node_match = re.match(r'([A-Za-z0-9]+)\[([^\]]+)\]', line)
        if node_match:
            node_id = node_match.group(1)
            label = node_match.group(2)
            nodes[node_id] = label
            continue
            
        # Parse connections: A --> B
        conn_match = re.match(r'([A-Za-z0-9]+)\s*-->\s*([A-Za-z0-9]+)', line)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            connections.append((from_node, to_node))
    
    if not nodes:
        return f'<div style="color: red; padding: 10px;">No valid nodes found in diagram</div>'
    
    # Calculate layout
    node_count = len(nodes)
    node_list = list(nodes.keys())
    
    # Better grid layout with more space
    cols = min(3, node_count)  # Max 3 columns for better readability
    rows = (node_count + cols - 1) // cols
    
    # SVG dimensions - larger for better visibility
    width = max(600, cols * 200)  # Minimum 600px width
    height = max(400, rows * 120 + 80)  # Minimum 400px height
    
    # Create SVG
    svg_content = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <style>
                .node {{ fill: #e3f2fd; stroke: #1976d2; stroke-width: 3; rx: 15; ry: 15; }}
                .node-text {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; text-anchor: middle; dominant-baseline: middle; fill: #1565c0; }}
                .arrow {{ stroke: #424242; stroke-width: 3; fill: none; marker-end: url(#arrowhead); }}
            </style>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#424242" />
            </marker>
        </defs>
    '''
    
    # Position nodes
    node_positions = {}
    for i, node_id in enumerate(node_list):
        col = i % cols
        row = i // cols
        x = col * 200 + 100  # More spacing between columns
        y = row * 120 + 80   # More spacing between rows
        node_positions[node_id] = (x, y)
        
        # Draw node
        label = nodes[node_id]
        text_width = len(label) * 8  # Better text width calculation
        rect_width = max(120, text_width + 30)  # Larger minimum width
        rect_height = 50  # Taller nodes
        
        svg_content += f'''
        <rect x="{x - rect_width//2}" y="{y - rect_height//2}" width="{rect_width}" height="{rect_height}" class="node" />
        <text x="{x}" y="{y}" class="node-text">{label}</text>
        '''
    
    # Draw connections
    for from_node, to_node in connections:
        if from_node in node_positions and to_node in node_positions:
            x1, y1 = node_positions[from_node]
            x2, y2 = node_positions[to_node]
            
            # Adjust for node size
            dx = x2 - x1
            dy = y2 - y1
            length = (dx*dx + dy*dy)**0.5
            if length > 0:
                # Normalize and scale - better arrow positioning
                dx = dx / length * 60  # Larger offset for bigger nodes
                dy = dy / length * 25
                
                svg_content += f'''
                <line x1="{x1 + dx}" y1="{y1 + dy}" x2="{x2 - dx}" y2="{y2 - dy}" class="arrow" />
                '''
    
    svg_content += '</svg>'
    
    return f'''<div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; text-align: center;">{svg_content}</div>'''

def process_markdown_with_simple_diagrams(markdown_text):
    """Process markdown and replace Mermaid code blocks with simple SVG diagrams"""
    # Find all Mermaid code blocks
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = list(re.finditer(mermaid_pattern, markdown_text, re.DOTALL))
    
    processed_text = markdown_text
    offset = 0
    
    for i, match in enumerate(matches):
        mermaid_code = match.group(1).strip()
        diagram_id = f"diagram-{int(random.random() * 1000000)}-{i}"
        
        # Create simple SVG diagram
        svg_html = create_simple_svg_diagram(mermaid_code, diagram_id)
        
        start = match.start() + offset
        end = match.end() + offset
        processed_text = processed_text[:start] + svg_html + processed_text[end:]
        offset += len(svg_html) - (end - start)
    
    return processed_text 