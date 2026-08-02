import os
import glob
import json
import logging
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_raw_file(filepath):
    """Parses a raw capture file and returns metadata and content."""
    metadata = {}
    content_lines = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_metadata = True
    for line in lines:
        if in_metadata:
            # Check for the separator
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
    return metadata, content

def get_classification(client, content):
    """Calls Groq API to classify content."""
    prompt = f"""
Analyze the following text and categorize it according to the PARA method (Projects, Areas, Resources, Archives).
Also provide a concise 1-2 sentence summary, and a list of up to 5 relevant tags (single words or short phrases).

Return the response STRICTLY as a JSON object with the following structure, and NO other text:
{{
  "category": "<one of: Projects, Areas, Resources, Archives>",
  "summary": "<summary text>",
  "tags": ["tag1", "tag2"]
}}

Text to analyze:
{content}
"""

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that analyzes and categorizes text data. Always respond in valid JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1, 
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON response: {response.choices[0].message.content}")
        return None

def process_files():
    raw_dir = os.path.join(os.path.dirname(__file__), 'raw')
    wiki_dir = os.path.join(os.path.dirname(__file__), 'wiki')
    os.makedirs(wiki_dir, exist_ok=True)
    
    raw_files = glob.glob(os.path.join(raw_dir, '*.txt'))
    
    if not raw_files:
        logging.info("No raw files to process.")
        return
        
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logging.error("GROQ_API_KEY environment variable not found. Please add it to your .env file.")
        return
        
    client = Groq(api_key=api_key)
    
    for filepath in raw_files:
        logging.info(f"Processing: {os.path.basename(filepath)}")
        metadata, content = parse_raw_file(filepath)
        
        if not content:
            logging.warning(f"File {filepath} is empty. Skipping.")
            continue
            
        classification = get_classification(client, content)
        
        if not classification:
            logging.error(f"Failed to classify {filepath}. Skipping.")
            continue
            
        # Extract variables
        item_id = metadata.get('id', 'unknown-id')
        timestamp = metadata.get('timestamp', 'unknown-timestamp')
        category = classification.get('category', 'Archives')
        summary = classification.get('summary', '')
        tags = classification.get('tags', [])
        
        # Format YAML tags string
        tags_str = "[" + ", ".join([f'"{tag}"' for tag in tags]) + "]"
        
        # Construct Markdown with YAML Frontmatter
        markdown_content = f"""---
id: {item_id}
timestamp: {timestamp}
category: {category}
tags: {tags_str}
summary: "{summary.replace('"', "'")}"
---

{content}
"""
        
        # Save to wiki/
        new_filename = f"{item_id}.md"
        new_filepath = os.path.join(wiki_dir, new_filename)
        
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        logging.info(f"Saved categorized file to: {new_filepath}")
        
        # Remove old file
        os.remove(filepath)
        logging.info(f"Removed original file: {filepath}")
        
if __name__ == "__main__":
    process_files()
