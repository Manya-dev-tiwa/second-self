import os
import re
import json
import yaml
from pathlib import Path

WIKI_DIR = "wiki"
GRAPH_FILE = "graph.json"

def build_graph():
    if not os.path.exists(WIKI_DIR):
        print(f"Error: {WIKI_DIR} directory not found.")
        return

    nodes = []
    edges = []
    
    # Regex to match [[uuid]]
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    for filename in os.listdir(WIKI_DIR):
        if not filename.endswith('.md'):
            continue
            
        file_path = os.path.join(WIKI_DIR, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse YAML frontmatter
        parts = content.split('---')
        if len(parts) >= 3:
            frontmatter_str = parts[1]
            body = '---'.join(parts[2:])
            
            try:
                metadata = yaml.safe_load(frontmatter_str)
                
                node_id = metadata.get('id', filename.replace('.md', ''))
                label = metadata.get('summary', 'Untitled')
                if len(label) > 50:
                    label = label[:47] + '...'
                    
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "group": metadata.get('category', 'Uncategorized'),
                    "title": metadata.get('summary', ''),
                    "tags": metadata.get('tags', [])
                })
                
                # Find all links in the body
                links = link_pattern.findall(body)
                for target_id in links:
                    edges.append({
                        "source": node_id,
                        "target": target_id.strip()
                    })
                    
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                
    graph_data = {
        "nodes": nodes,
        "edges": edges
    }
    
    with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=4)
        
    print(f"Graph successfully built with {len(nodes)} nodes and {len(edges)} edges.")
    print(f"Saved to {GRAPH_FILE}")

if __name__ == "__main__":
    build_graph()
