# SecondSelf — Phase-Wise Implementation Plan

This document breaks down the development of the **SecondSelf** personal AI second brain into four distinct phases, aligning with the project's week-by-week structure and technical architecture. 

Each phase builds upon the outputs of the previous phase.

## Phase 1: The Archivist (Capture Pipeline)
**Goal:** Establish the foundation to ingest and persistently store unstructured knowledge.

### 1.1 Scaffold Project Structure
- Initialize the Python environment.
- Create core directories: `raw/` (for unclassified data) and `wiki/` (for structured, linked data).
- Define project dependencies (`streamlit`, `sentence-transformers`, `groq`, `streamlit-agraph`) in `requirements.txt`.

### 1.2 Implement the Ingestion Engine (`capture.py`)
- **Features:** 
  - A CLI tool to capture notes, URLs, or file contents.
  - Generates a unique UUID and an ISO timestamp for every item.
- **Output:** Raw text files saved to the `raw/` folder, structured with metadata headers.

### 1.3 Validation
- Test the script by capturing 10+ real-world items (ideas, articles, tasks, meeting notes) into `raw/`.

---

## Phase 2: The Librarian (AI Classification & Linking)
**Goal:** Automate the organization and linking of raw knowledge using LLMs and embeddings.

### 2.1 Auto-Classify (The Sorting Hat - `classify.py`)
- **Integration:** Connect to Groq/Llama 3 API.
- **Process:** Iterate through unclassified text files in `raw/`. Prompt the LLM to extract a summary, relevant tags, and a category based on the PARA method (Projects, Areas, Resources, Archives).
- **Output:** Move and transform these items into Markdown files (`.md`) inside the `wiki/` folder, utilizing YAML frontmatter to store the extracted metadata.

### 2.2 Auto-Link (Connect the Dots - `link.py`)
- **Integration:** Setup local embeddings using `sentence-transformers`.
- **Process:** Compute vector embeddings for all notes inside `wiki/`. 
- **Analysis:** Compare each note against others using cosine similarity. If the similarity surpasses a predefined threshold (e.g., 0.70), inject explicit Markdown links (`[[unique_id]]`) between them.
- **Output:** A fully interconnected web of markdown files in `wiki/`.

### 2.3 Validation
- Run the pipeline on the initial 10+ captures and ensure the `wiki/` folder is correctly populated with structured, linked documents.

---

## Phase 3: The Cartographer (Knowledge Graph)
**Goal:** Visually map the connected knowledge base to allow interactive exploration.

### 3.1 Graph Data Model (`build_graph.py`)
- **Process:** Parse all `.md` files in the `wiki/` directory. Extract nodes (individual notes) and edges (the injected `[[links]]`).
- **Output:** Generate a `graph.json` file containing the nodes and edges array.

### 3.2 Visualization Prep
- Ensure the JSON structure strictly matches the expected input format for the downstream UI graph library (`streamlit-agraph` or `vis-network`).

### 3.3 Validation
- Inspect `graph.json` to verify node presence, edge accuracy, and structural integrity.

---

## Phase 4: The Oracle (Querying & Deployment)
**Goal:** Implement retrieval-augmented natural language search and expose the system via a web UI.

### 4.1 RAG Engine (`ask.py`)
- **Process:** Vectorize the user's plain-English question. Perform a similarity search against the embedded `wiki/` notes to find the most relevant context.
- **Synthesis:** Pass the user's question and the retrieved context to the LLM to synthesize an accurate, localized answer.

### 4.2 Web Interface (`app.py`)
- **UI Framework:** Build a `Streamlit` dashboard.
- **Components:**
  1. An interactive, force-directed graph view powered by `graph.json` allowing hover, drag, and zoom capabilities.
  2. A chat/search interface wired to the `ask.py` function.

### 4.3 Deployment
- Deploy the unified Streamlit application to Streamlit Community Cloud or HuggingFace Spaces to make it accessible via a public URL.

### 4.4 Validation
- Verify the end-to-end pipeline: Capture -> Classify -> Link -> Graph -> Ask.
- Test the live URL to ensure UI responsiveness and RAG query accuracy.
