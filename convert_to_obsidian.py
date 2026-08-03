import json
import os
from pathlib import Path

def load_graph():
    """Load the knowledge graph from graph.json"""
    graph_file = os.path.join(os.path.dirname(__file__), 'graph.json')
    with open(graph_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def sanitize_filename(text, node_id):
    """Sanitize text for use as filename, using node_id for uniqueness"""
    # Remove invalid characters and truncate
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '')
    # Use first few chars of node_id to ensure uniqueness
    unique_suffix = node_id[:8]
    # Limit length and add unique suffix
    base_name = text[:30] if text else "untitled"
    return f"{base_name}_{unique_suffix}"

def convert_to_obsidian():
    """Convert graph.json to Obsidian markdown files (optimized for performance)"""
    graph = load_graph()
    
    # Create obsidian vault directory
    vault_dir = Path(os.path.join(os.path.dirname(__file__), 'obsidian_vault'))
    vault_dir.mkdir(exist_ok=True)
    
    # Create mappings for efficient lookups
    node_to_filename = {}
    node_lookup = {node['id']: node for node in graph['nodes']}  # O(1) node lookup
    
    # Build adjacency list for connections
    connections = {}
    for edge in graph['edges']:
        source = edge['source']
        target = edge['target']
        
        if source not in connections:
            connections[source] = []
        if target not in connections:
            connections[target] = []
        
        connections[source].append(target)
        connections[target].append(source)
    
    # Single pass: create all markdown files with complete content
    for node in graph['nodes']:
        # Create filename from label with unique ID suffix
        filename = sanitize_filename(node['label'], node['id'])
        node_to_filename[node['id']] = f"{filename}.md"
        
        # Create markdown content
        content = f"# {node['title']}\n\n"
        content += f"{node['label']}\n\n"
        
        # Add tags
        if node.get('tags'):
            tags = ' '.join([f"#{tag.replace(' ', '-')}" for tag in node['tags']])
            content += f"Tags: {tags}\n\n"
        
        # Add group/category
        if node.get('group'):
            content += f"Category: {node['group']}\n\n"
        
        # Add links section (pre-computed)
        content += "---\n\n## Links\n\n"
        
        # Add links if this node has connections
        if node['id'] in connections:
            for connected_id in connections[node['id']]:
                if connected_id in node_to_filename:
                    target_filename = node_to_filename[connected_id].replace('.md', '')
                    content += f"- [[{target_filename}]]\n"
        
        # Write file (single write per file)
        filepath = vault_dir / node_to_filename[node['id']]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Successfully converted {len(graph['nodes'])} notes to Obsidian format!")
    print(f"Files created in: {vault_dir.absolute()}")
    print(f"\nNext steps:")
    print(f"1. Open Obsidian")
    print(f"2. Create a new vault or open an existing one")
    print(f"3. Copy the files from: {vault_dir.absolute()}")
    print(f"4. Paste them into your Obsidian vault folder")
    print(f"5. The graph view will automatically show the connections!")

if __name__ == "__main__":
    convert_to_obsidian()
