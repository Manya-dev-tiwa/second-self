# SecondSelf — Edge Cases and Corner Scenarios

This document outlines potential edge cases, failure modes, and corner scenarios for the SecondSelf project, categorized by system phase. Anticipating these scenarios will help build a more resilient system.

## Phase 1: The Archivist (Capture Pipeline)

### 1. Ingestion Failures
- **Empty Inputs:** User runs the capture command with empty strings or whitespace-only inputs.
- **Massive Files:** User attempts to capture extremely large files (e.g., a 100MB log file), which could cause memory crashes during read/write.
- **Non-Text Binaries:** User passes paths to images, PDFs, or executables. The script currently expects text. Reading these with `utf-8` encoding will throw errors.
- **URL Scraping Blocks:** Captured links that require authentication, CAPTCHAs, or heavily use JavaScript to render content, resulting in empty or generic error text instead of the actual article.
- **Special Characters in Paths:** User inputs containing illegal characters for Windows/Linux filenames or paths.

## Phase 2: The Librarian (AI Classification & Auto-Linking)

### 1. Classification (LLM) Bottlenecks
- **API Rate Limits & Downtime:** Hitting rate limits on the free tier of Groq or Llama 3 API, causing the classification pipeline to fail mid-batch.
- **Context Window Overflow:** Capturing an extremely long article that exceeds the maximum token limit of the classification LLM.
- **Hallucinated Output:** The LLM returns a category outside the strict PARA method (e.g., "Miscellaneous") or malformed JSON/YAML that breaks the frontmatter parser.

### 2. Auto-Linking (Embeddings) Scenarios
- **The "Hairball" Problem:** A generic note (e.g., "technology is good") that matches almost everything, creating excessive edges and cluttering the graph.
- **Isolated Nodes (Orphans):** A highly niche note that meets zero similarity thresholds with any other note, leaving it entirely disconnected.
- **Self-Linking:** The similarity check incorrectly evaluating a note against itself and injecting a recursive self-link.
- **Token Limits on Embeddings:** `sentence-transformers` models typically truncate text over 512 tokens. Crucial information at the end of a long note might never be embedded or linked.

## Phase 3: The Cartographer (Knowledge Graph)

### 1. Rendering and Data Structure
- **Performance Degradation (UI Lag):** The graph library (`vis-network` / `Cytoscape`) freezing or dropping frames when rendering thousands of nodes and edges simultaneously.
- **Malformed Markdown Links:** Regex parsers in `build_graph.py` failing on edge-case link formats (e.g., `[[ note_id ]]` with spaces, or `[[id|alias]]`).
- **Mobile Unusability:** Force-directed graphs often fail to scale well on touch screens or small viewports.

## Phase 4: The Oracle (Querying & UI)

### 1. RAG and Query Responses
- **Out-of-Domain Queries:** The user asks a question completely unrelated to any captured notes (e.g., "What is the capital of France?"). The LLM might hallucinate an answer from its base training instead of admitting the brain lacks the info.
- **Context Dilution:** The RAG retrieval pulls in the top 5 most similar notes, but the combined text is too long and exceeds the LLM's context window for the final answer generation.
- **Irrelevant Retrieval:** The embeddings surface notes that use similar words but have completely different semantic meanings, leading to nonsensical answers.
- **Concurrency Issues:** Multiple users querying the Streamlit public URL simultaneously, potentially causing state leaks or race conditions if the session state isn't managed properly.
