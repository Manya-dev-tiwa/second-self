import argparse
import uuid
import datetime
import os
import urllib.parse

def capture(input_data):
    """
    Captures a note, link, or file into the raw/ directory.
    """
    unique_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    # Windows paths can't contain colons, replace them
    safe_timestamp = timestamp.replace(':', '-')
    
    raw_dir = os.path.join(os.path.dirname(__file__), 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    filename = f"{safe_timestamp}_{unique_id}.txt"
    filepath = os.path.join(raw_dir, filename)
    
    content_to_save = ""
    
    # Check if input is a file
    if os.path.isfile(input_data):
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                content_to_save = f.read()
            print(f"Detected file. Reading content from {input_data}")
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # Treat as note or link
        content_to_save = input_data
        
    # Check if it's a link (simple heuristic)
    parsed = urllib.parse.urlparse(input_data)
    if parsed.scheme in ('http', 'https'):
        print("Detected link.")
        # We could fetch the content here, but for now we just save the link
    
    # Save the raw content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"ID: {unique_id}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("-" * 40 + "\n")
        f.write(content_to_save)
        
    print(f"Successfully captured to raw/{filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture notes, links, or files into the Second Brain.")
    parser.add_argument("input", help="The text, link, or path to a file to capture.")
    
    args = parser.parse_args()
    capture(args.input)
