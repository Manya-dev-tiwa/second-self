import os
import re
import json
import yaml
import math
import random
from pathlib import Path

WIKI_DIR = "wiki"
GRAPH_FILE = "graph.json"

def compute_layout(nodes, edges, new_node_ids, iterations=50):
    """
    Computes a force-directed layout for the nodes.
    Locks the positions of existing nodes, and only calculates coordinates for new nodes
    so that they naturally align with their neighbors while preserving existing stability.
    """
    w = 800
    h = 600
    
    # Initialize positions of existing nodes if they lack coordinates, and find new nodes
    existing_pos = {}
    for node in nodes:
        if node["id"] not in new_node_ids and "x" in node and "y" in node:
            existing_pos[node["id"]] = (node["x"], node["y"])
            
    # For new nodes or nodes without coordinates, initialize them near neighbors or in a spiral
    for i, node in enumerate(nodes):
        nid = node["id"]
        if "x" not in node or "y" not in node or nid in new_node_ids:
            # Try to place near neighbors
            neighbors = []
            for edge in edges:
                if edge["source"] == nid and edge["target"] in existing_pos:
                    neighbors.append(existing_pos[edge["target"]])
                elif edge["target"] == nid and edge["source"] in existing_pos:
                    neighbors.append(existing_pos[edge["source"]])
            
            if neighbors:
                # Place at average neighbor position with small offset
                avg_x = sum(p[0] for p in neighbors) / len(neighbors)
                avg_y = sum(p[1] for p in neighbors) / len(neighbors)
                node["x"] = avg_x + random.uniform(-20, 20)
                node["y"] = avg_y + random.uniform(-20, 20)
            else:
                # Place in a spiral from center
                r = 100.0 + i * 20.0
                theta = i * 0.5
                node["x"] = r * math.cos(theta)
                node["y"] = r * math.sin(theta)
                
    if not new_node_ids:
        # If there are no new nodes, we might just be doing a first-time run for all nodes
        # In that case, let's treat all nodes as simulated
        sim_node_ids = {node["id"] for node in nodes}
    else:
        # Only simulate positions for the new nodes
        sim_node_ids = set(new_node_ids)

    # Ideal distance
    area = w * h
    k = math.sqrt(area / max(len(nodes), 1))
    
    # Temperature
    temp = w / 15.0
    dt = temp / iterations
    
    # Setup coordinates dictionary
    pos = {node["id"]: [node["x"], node["y"]] for node in nodes}
    edge_list = [(edge["source"], edge["target"]) for edge in edges if edge["source"] in pos and edge["target"] in pos]
    
    for _ in range(iterations):
        disp = {nid: [0.0, 0.0] for nid in pos}
        
        # Repulsion between all nodes
        nids = list(pos.keys())
        for i in range(len(nids)):
            u = nids[i]
            for j in range(i + 1, len(nids)):
                v = nids[j]
                
                # We only need forces if at least one node is simulated
                if u not in sim_node_ids and v not in sim_node_ids:
                    continue
                    
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 0.1
                    
                fr = (k * k) / dist
                
                # Update displacement for simulated nodes
                if u in sim_node_ids:
                    disp[u][0] += (dx / dist) * fr
                    disp[u][1] += (dy / dist) * fr
                if v in sim_node_ids:
                    disp[v][0] -= (dx / dist) * fr
                    disp[v][1] -= (dy / dist) * fr
                    
        # Attraction along edges
        for u, v in edge_list:
            if u not in sim_node_ids and v not in sim_node_ids:
                continue
                
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 0.1
                
            fa = (dist * dist) / k
            
            if u in sim_node_ids:
                disp[u][0] -= (dx / dist) * fa
                disp[u][1] -= (dy / dist) * fa
            if v in sim_node_ids:
                disp[v][0] += (dx / dist) * fa
                disp[v][1] += (dy / dist) * fa
                
        # Update coordinates for simulated nodes
        for nid in sim_node_ids:
            dx, dy = disp[nid]
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
                
            lim_dist = min(dist, temp)
            pos[nid][0] += (dx / dist) * lim_dist
            pos[nid][1] += (dy / dist) * lim_dist
            
            # Constrain to layout area
            pos[nid][0] = max(-w, min(w, pos[nid][0]))
            pos[nid][1] = max(-h, min(h, pos[nid][1]))
            
        temp -= dt
        
    # Write back coordinates
    for node in nodes:
        node["x"] = round(pos[node["id"]][0], 1)
        node["y"] = round(pos[node["id"]][1], 1)

def build_graph():
    if not os.path.exists(WIKI_DIR):
        print(f"Error: {WIKI_DIR} directory not found.")
        return

    # 1. Load existing graph
    existing_nodes = []
    existing_edges = []
    if os.path.exists(GRAPH_FILE):
        try:
            with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
                existing_nodes = graph_data.get("nodes", [])
                existing_edges = graph_data.get("edges", [])
        except Exception as e:
            print(f"Error loading {GRAPH_FILE}: {e}")
            
    # Maps for lookup
    node_map = {n["id"]: n for n in existing_nodes}
    
    current_node_ids = set()
    new_node_ids = set()
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    # Track nodes updated/added in this run
    parsed_edges = []
    
    # 2. Scan wiki files
    for filename in os.listdir(WIKI_DIR):
        if not filename.endswith('.md'):
            continue
            
        file_path = os.path.join(WIKI_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parts = content.split('---')
        if len(parts) >= 3:
            frontmatter_str = parts[1]
            body = '---'.join(parts[2:])
            
            try:
                metadata = yaml.safe_load(frontmatter_str)
                node_id = metadata.get('id', filename.replace('.md', ''))
                current_node_ids.add(node_id)
                
                label = metadata.get('summary', 'Untitled')
                if len(label) > 50:
                    label = label[:47] + '...'
                
                # Check if it is a new node or existing node
                if node_id in node_map:
                    # Update existing node metadata in place
                    node = node_map[node_id]
                    node["label"] = label
                    node["group"] = metadata.get('category', 'Uncategorized')
                    node["title"] = metadata.get('summary', '')
                    node["tags"] = metadata.get('tags', [])
                else:
                    # Create new node
                    node = {
                        "id": node_id,
                        "label": label,
                        "group": metadata.get('category', 'Uncategorized'),
                        "title": metadata.get('summary', ''),
                        "tags": metadata.get('tags', [])
                    }
                    new_node_ids.add(node_id)
                    node_map[node_id] = node
                
                # Extract links from body
                links = link_pattern.findall(body)
                for target_id in links:
                    target_id = target_id.strip()
                    parsed_edges.append((node_id, target_id))
                    
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                
    # 3. Clean up deleted nodes (nodes whose files no longer exist in WIKI_DIR)
    nodes = [node_map[nid] for nid in node_map if nid in current_node_ids]
    
    # Rebuild edges incrementally
    # First, preserve existing edges where both endpoints still exist
    edges = []
    for edge in existing_edges:
        src = edge["source"]
        tgt = edge["target"]
        if src in current_node_ids and tgt in current_node_ids:
            edges.append(edge)
            
    # Set of existing edge endpoints for checking duplicates
    edge_pairs_undirected = set()
    for e in edges:
        edge_pairs_undirected.add((e["source"], e["target"]))
        edge_pairs_undirected.add((e["target"], e["source"]))
    
    # Append new parsed edges if they don't already exist and endpoints are valid
    for src, tgt in parsed_edges:
        if src in current_node_ids and tgt in current_node_ids:
            if (src, tgt) not in edge_pairs_undirected:
                edges.append({"source": src, "target": tgt})
                edge_pairs_undirected.add((src, tgt))
                edge_pairs_undirected.add((tgt, src))
                
    # 4. Compute layouts for new nodes, preserving existing coordinates
    compute_layout(nodes, edges, new_node_ids)
    
    # 5. Save the updated graph
    graph_data = {
        "nodes": nodes,
        "edges": edges
    }
    
    with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=4)
        
    print(f"Graph successfully updated incrementally.")
    print(f"Total: {len(nodes)} nodes ({len(new_node_ids)} new), {len(edges)} edges.")
    print(f"Saved to {GRAPH_FILE}")

if __name__ == "__main__":
    build_graph()
