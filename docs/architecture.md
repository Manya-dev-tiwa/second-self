# SecondSelf — Personal AI Second Brain Architecture

This document outlines the detailed technical architecture for the **SecondSelf** system.

## Proposed Architecture

```mermaid
flowchart TD
    subgraph Capture Layer
        C[capture.py]
    end

    subgraph Storage Layer
        R[(raw/)]
        W[(wiki/)]
        G[(graph.json)]
    end

    subgraph Processing Layer (AI)
        CL[classify.py\nLLM: Groq/Llama3]
        L[link.py\nLocal Embeddings]
        BG[build_graph.py]
    end

    subgraph Serving Layer
        A[ask.py\nRAG Pipeline]
        UI[app.py\nStreamlit UI]
    end

    C -- "Saves raw file/link/note" --> R
    R -- "Reads raw data" --> CL
    CL -- "Adds PARA & Summary" --> W
    W -- "Reads wiki notes" --> L
    L -- "Adds links between notes" --> W
    W -- "Reads wiki & links" --> BG
    BG -- "Generates Graph" --> G
    
    G -- "Displays Visual Brain" --> UI
    W -- "Vector Search Context" --> A
    A -- "Answers Queries" --> UI
```

## System Components

We will build the system iteratively over 4 weeks as per the requirements.

### Week 1: Capture Pipeline
Sets up the foundation for capturing unstructured information.

- **capture.py**: CLI script to ingest text, links, or files. Generates a unique ID and saves the content to `raw/<id>.txt`.

### Week 2: AI Classification & Auto-linking
The core intelligence engine that organizes information automatically.

- **classify.py**: Reads unprocessed items from `raw/`. Prompts an LLM (Groq) to classify the content into PARA categories. Extracts tags and generates a 1-line summary. Moves/saves the enriched note into `wiki/<id>.md` with YAML frontmatter containing the metadata.
- **link.py**: Reads all files in `wiki/`. Computes dense vector embeddings using `sentence-transformers`. Calculates cosine similarity between all pairs of notes. If similarity > threshold (e.g., 0.7), injects a link (e.g., `[[id2]]`) into the note.

### Week 3: Knowledge Graph
Transforms the wiki into an interactive visual representation.

- **build_graph.py**: Parses `wiki/` markdown files. Identifies nodes (notes) and edges (links). Outputs the structure to `graph.json` formatted for UI consumption.

### Week 4: Ask & Streamlit UI
The user-facing application for querying and exploring the second brain.

- **ask.py**: A Retrieval-Augmented Generation (RAG) function. Converts the user's question into an embedding. Retrieves the top-K most relevant notes from `wiki/`. Prompts the LLM to answer the question using *only* the retrieved context.
- **app.py**: Streamlit application serving as the frontend. Renders `graph.json` interactively. Provides a chat interface that calls `ask.py`.
