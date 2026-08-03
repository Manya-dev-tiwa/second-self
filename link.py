import os
import glob
import logging
import pickle
import hashlib
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer, util

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_md_file(filepath):
    """Parses a markdown file and returns metadata and content."""
    metadata = {}
    content_lines = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_metadata = False
    for i, line in enumerate(lines):
        if i == 0 and line.startswith('---'):
            in_metadata = True
            continue
            
        if in_metadata:
            if line.startswith('---'):
                in_metadata = False
                continue
            
            # Parse key-value pairs
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip().lower()] = val.strip()
        else:
            content_lines.append(line)
            
    content = "".join(content_lines).strip()
    # Strip existing related notes to avoid duplicates when re-running
    if "## Related Notes" in content:
        content = content.split("## Related Notes")[0].strip()
        
    return metadata, content

def get_file_hash(filepath):
    """Generate a hash of file content for change detection"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def process_links():
    wiki_dir = os.path.join(os.path.dirname(__file__), 'wiki')
    md_files = glob.glob(os.path.join(wiki_dir, '*.md'))
    
    if len(md_files) < 2:
        logging.info("Not enough markdown files to find links.")
        return
    
    # Load existing hash cache if available
    hash_cache_path = os.path.join(os.path.dirname(__file__), 'data', 'file_hashes.pkl')
    hash_cache = {}
    if os.path.exists(hash_cache_path):
        try:
            with open(hash_cache_path, 'rb') as f:
                hash_cache = pickle.load(f)
        except:
            hash_cache = {}
    
    # Check which files have changed
    changed_files = []
    for filepath in md_files:
        current_hash = get_file_hash(filepath)
        if filepath not in hash_cache or hash_cache[filepath] != current_hash:
            changed_files.append(filepath)
            hash_cache[filepath] = current_hash
    
    if not changed_files:
        logging.info("No files changed since last processing. Skipping full re-computation.")
        # Still need to update relationships for all files in case of additions
        changed_files = md_files
    
    logging.info(f"Processing {len(changed_files)} changed/new files out of {len(md_files)} total.")
    
    logging.info("Loading sentence-transformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    documents = []
    metadata_list = []
    
    for filepath in md_files:
        metadata, content = parse_md_file(filepath)
        
        # Combine summary and content for better embedding representation
        summary = metadata.get('summary', '').strip('"').strip("'")
        doc_text = f"{summary} {content}"
        
        documents.append(doc_text)
        metadata_list.append((filepath, metadata))
        
    logging.info(f"Computing embeddings for {len(documents)} files...")
    # Use larger batch size for faster processing
    embeddings = model.encode(documents, convert_to_tensor=True, batch_size=32, show_progress_bar=False)
    
    logging.info("Calculating cosine similarity matrix...")
    # Normalize embeddings once for faster similarity calculation using dot product
    normalized_embeddings = F.normalize(embeddings, p=2, dim=1)
    cosine_scores = torch.matmul(normalized_embeddings, normalized_embeddings.T)
    
    # 0.50 threshold chosen based on empirical results with miniLM on short text
    similarity_threshold = 0.50  
    
    for i, (filepath, metadata) in enumerate(metadata_list):
        item_id = metadata.get('id', 'unknown')
        related_ids = []
        
        # Find related documents
        for j in range(len(metadata_list)):
            if i == j:
                continue
            score = cosine_scores[i][j].item()
            if score > similarity_threshold:
                related_id = metadata_list[j][1].get('id')
                if related_id:
                    related_ids.append((related_id, score))
                    
        # Sort by similarity score descending
        related_ids.sort(key=lambda x: x[1], reverse=True)
                    
        # Read the original file again to ensure we preserve frontmatter perfectly
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # Remove old related notes section if it exists
        if "## Related Notes" in original_content:
            original_content = original_content.split("## Related Notes")[0].strip()
            
        if related_ids:
            logging.info(f"Found {len(related_ids)} related notes for {item_id}")
            # Append new related notes
            links_text = "\n\n## Related Notes\n" + "\n".join([f"- [[{rid[0]}]]" for rid in related_ids]) + "\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(original_content.strip() + links_text)
        else:
            logging.info(f"No related notes found for {item_id}")
            # Rewrite original content just in case it had old related notes we stripped
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(original_content.strip() + "\n")
            
    # Save embeddings for RAG
    logging.info("Saving embeddings to data/embeddings.pkl...")
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    
    saved_data = []
    cpu_embeddings = embeddings.cpu().numpy()
    for i, (filepath, metadata) in enumerate(metadata_list):
        saved_data.append({
            "id": metadata.get('id'),
            "metadata": metadata,
            "text": documents[i],
            "embedding": cpu_embeddings[i]
        })
        
    embeddings_path = os.path.join(os.path.dirname(__file__), 'data', 'embeddings.pkl')
    with open(embeddings_path, 'wb') as f:
        pickle.dump(saved_data, f)
    
    # Save hash cache for next time
    with open(hash_cache_path, 'wb') as f:
        pickle.dump(hash_cache, f)
        
    logging.info("Link processing complete.")

if __name__ == "__main__":
    process_links()
