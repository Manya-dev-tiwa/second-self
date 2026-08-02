import pickle
import os

def main():
    file_path = os.path.join("data", "embeddings.pkl")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
        
    try:
        with open(file_path, "rb") as f:
            embeddings = pickle.load(f)
            
        print(f"Successfully loaded embeddings from {file_path}")
        print("-" * 50)
        
        if isinstance(embeddings, dict):
            print(f"Found {len(embeddings)} entries.")
            for key, value in list(embeddings.items())[:5]: # Show first 5 for brevity
                print(f"Key: {key}")
                if hasattr(value, "shape"):
                    print(f"Value Shape: {value.shape}")
                else:
                    print(f"Value: {value[:5]}... (truncated for brevity)")
                print("-" * 20)
            
            if len(embeddings) > 5:
                print(f"... and {len(embeddings) - 5} more entries.")
                
        elif isinstance(embeddings, list):
            print(f"Found {len(embeddings)} entries in a list.")
            for i, item in enumerate(embeddings[:5]):
                print(f"Item {i}:")
                if hasattr(item, "shape"):
                    print(f"Shape: {item.shape}")
                else:
                    print(f"Content: {str(item)[:100]}...")
            
            if len(embeddings) > 5:
                print(f"... and {len(embeddings) - 5} more entries.")
                
        else:
            print(f"Type of embeddings: {type(embeddings)}")
            print("Content:")
            print(embeddings)
            
    except Exception as e:
        print(f"Failed to load the pickle file: {e}")

if __name__ == "__main__":
    main()
