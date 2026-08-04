import os
import pickle
import numpy as np
import torch
import torch.nn.functional as F
import threading
from sentence_transformers import SentenceTransformer, util
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize models
EMBEDDINGS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'embeddings.json')
EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'embeddings.pkl')

class RAGEngine:
    _encoder = None  # Class-level cache for the encoder model
    _encoder_lock = threading.Lock()
    _groq_client = None  # Class-level cache for Groq client
    
    def __init__(self):
        self.data = None
        self.embeddings_tensor = None
        
        # We will lazy-load the encoder to speed up initial app start if it's not used immediately
        self._load_data()
        
    def _load_data(self):
        import json
        # Prefer JSON for platform and python version independence
        if os.path.exists(EMBEDDINGS_JSON_PATH):
            try:
                with open(EMBEDDINGS_JSON_PATH, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)

                if not self.data:
                    print("Embeddings JSON file is empty. No data loaded.")
                    self.embeddings_tensor = None
                    return

                # Convert list of embeddings to a single numpy array then to tensor
                embeds = np.array([item["embedding"] for item in self.data])
                self.embeddings_tensor = torch.tensor(embeds)
                print(f"Successfully loaded {len(self.data)} embeddings from JSON.")
                return
            except Exception as e:
                print(f"Error loading JSON embeddings: {e}. Falling back to pickle...")

        # Fallback to pickle
        if not os.path.exists(EMBEDDINGS_PATH):
            print("No embeddings found. Please run link.py first to generate embeddings.")
            self.data = []
            self.embeddings_tensor = None
            return

        try:
            with open(EMBEDDINGS_PATH, 'rb') as f:
                self.data = pickle.load(f)

            if not self.data:
                print("Embeddings file is empty. No data loaded.")
                self.embeddings_tensor = None
                return

            # Convert list of embeddings to a single numpy array then to tensor if needed
            embeds = np.array([item["embedding"] for item in self.data])
            self.embeddings_tensor = torch.tensor(embeds)
            print(f"Successfully loaded {len(self.data)} embeddings from pickle.")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            self.data = []
            self.embeddings_tensor = None
    
    def reload_data(self):
        """Force reload of embeddings data - useful after processing new captures"""
        self.data = None
        self.embeddings_tensor = None
        if hasattr(self, '_normalized_embeddings'):
            del self._normalized_embeddings
        self._load_data()
    
    @classmethod
    def clear_encoder_cache(cls):
        """Clear the cached encoder model - useful for memory management"""
        cls._encoder = None
        cls._groq_client = None
        
    def _get_encoder(self):
        # Use class-level cache with thread-safe initialization
        if RAGEngine._encoder is None:
            with RAGEngine._encoder_lock:
                if RAGEngine._encoder is None:
                    RAGEngine._encoder = SentenceTransformer('all-MiniLM-L6-v2')
        return RAGEngine._encoder
        
    def _get_groq_client(self):
        # Use class-level cache for Groq client
        if RAGEngine._groq_client is None:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY environment variable is missing. "
                    "Please set it in your environment or Streamlit secrets."
                )
            try:
                RAGEngine._groq_client = Groq(api_key=api_key)
            except Exception as e:
                raise ValueError(f"Failed to initialize Groq client: {e}")
        return RAGEngine._groq_client

    def search(self, query: str, top_k: int = 3):
        if not self.data or self.embeddings_tensor is None:
            return []

        encoder = self._get_encoder()
        # Use batch processing for better performance and disable progress bar
        query_embedding = encoder.encode([query], convert_to_tensor=True, show_progress_bar=False, normalize_embeddings=True)

        # Normalize embeddings for faster cosine similarity
        if not hasattr(self, '_normalized_embeddings'):
            self._normalized_embeddings = F.normalize(self.embeddings_tensor, p=2, dim=1)

        # Calculate cosine similarity using dot product (faster for normalized vectors)
        cos_scores = torch.matmul(query_embedding, self._normalized_embeddings.T)[0]

        # Get top k results
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.data)))

        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            item = self.data[idx]
            results.append({
                "id": item["id"],
                "text": item["text"],
                "score": score.item(),
                "metadata": item["metadata"]
            })

        return results
        
    def ask(self, query: str) -> str:
        results = self.search(query, top_k=3)

        if not results:
            if not self.data:
                return "No knowledge base is available. Please add some notes and generate embeddings first."
            return "I couldn't find any relevant information in your Second Brain to answer that."

        # Construct context
        context_parts = []
        for i, res in enumerate(results):
            context_parts.append(f"Document {i+1}:\n{res['text']}\n")

        context = "\n".join(context_parts)

        prompt = f"""You are SecondSelf, a personal AI assistant answering questions based on the user's notes.
Use ONLY the provided context to answer the query. If the answer is not in the context, say so. Do not use outside knowledge.

Context:
{context}

Question: {query}

Answer:"""

        try:
            client = self._get_groq_client()
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.1-8b-instant",
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    import sys
    engine = RAGEngine()
    
    # Get question from command line argument or use default
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = "What is the project about?"
    
    print(f"Q: {q}")
    print(engine.ask(q))
