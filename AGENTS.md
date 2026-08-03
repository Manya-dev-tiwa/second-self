# SecondSelf - Agent Configuration

## Project Information
This is a premium AI SaaS dashboard for personal knowledge management, built with Streamlit.

## Build & Run Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Build knowledge graph
python build_graph.py

# Convert to Obsidian format
python convert_to_obsidian.py
```

### Deployment
```bash
# Streamlit Cloud (Recommended)
# 1. Push to GitHub
# 2. Connect to Streamlit Cloud
# 3. Set GROQ_API_KEY in secrets
# 4. Deploy

# Docker deployment
docker build -t secondself .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key secondself

# Docker Compose
docker-compose up -d

# Railway/Render
# Use Procfile and railway.json for deployment
```

### Testing
```bash
# Test RAG engine
python ask.py "What is the project about?"

# View embeddings
python view_embeddings.py
```

## Key Files
- `app.py` - Main Streamlit application with premium UI
- `ask.py` - RAG engine (backend logic - kept unchanged)
- `build_graph.py` - Knowledge graph construction
- `graph.json` - Knowledge graph data
- `data/embeddings.pkl` - Pre-computed embeddings
- `.streamlit/config.toml` - Streamlit configuration
- `requirements.txt` - Python dependencies with pinned versions
- `Procfile` - For Railway/Render deployment
- `Dockerfile` - For Docker deployment
- `deployment-plan.md` - Comprehensive deployment guide

## Dependencies
- streamlit>=1.28.0,<2.0.0
- sentence-transformers>=2.2.0,<3.0.0
- groq>=0.4.0,<1.0.0
- streamlit-agraph>=0.0.45,<1.0.0
- python-dotenv>=1.0.0,<2.0.0
- torch>=2.0.0,<3.0.0
- numpy>=1.24.0,<2.0.0

## Environment Variables
- GROQ_API_KEY - Required for AI responses

## Deployment Configuration Files
- `.streamlit/config.toml` - Streamlit app configuration
- `.streamlit/secrets.toml.example` - Template for API keys
- `.gitignore` - Updated to exclude sensitive files
- `Procfile` - For cloud platform deployment
- `railway.json` - Railway-specific configuration
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Docker Compose setup
- `.dockerignore` - Docker build exclusions

## Deployment Optimizations
- Lazy loading of heavy imports to improve cold start
- Streamlit resource caching for RAG engine
- Graph data caching with TTL
- Graceful error handling for missing data
- Environment variable validation
- Optimized embeddings loading with better error messages

## UI Features Implemented
- Fixed sidebar with navigation
- Modern card components with glassmorphism
- Interactive knowledge graph visualization
- Chat-style interface with animations
- Statistics dashboard
- Professional dark theme
- Responsive layout
- Smooth animations and transitions

## Backend Logic
The backend logic in `ask.py` has been kept unchanged as requested:
- RAGEngine class with search and ask methods
- Sentence transformer embeddings
- Groq API integration
- Cosine similarity search
- Enhanced error handling for production
