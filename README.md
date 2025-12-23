# Deep Insight Scholar

Name: Manoj B
Email: manoj2882003@gmail.com

## Design Overview

The system is designed to be modular, with clear separations of concern across modules. The core preprocessing pipeline is divided into four main stages:

1. **Document Processing**: Loads PDFs, extracts text, and removes document-level noise.
2. **Structuring**: Extracts logical paper sections (Abstract, Introduction, Methodology, etc.) and builds a unified `ResearchPaper` object.
3. **Chunking**: Divides sections into semantically meaningful units with metadata.
4. **Embedding**: Generates embeddings for chunks using a selected embedding model.

The system uses adapter-based integration with LangChain to convert internal chunk representations into LangChain `Document` objects for vector indexing. The FAISS vector store is used for efficient similarity search and retrieval.

Deep Insight Scholar is a modular research paper processing and semantic search system.  
It ingests research PDFs, extracts structured sections, builds a unified paper representation, and enables semantic retrieval over section-aware chunks.

---
## How to run

```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python demo1.py

```

## Project Structure

```

DEEP_INSIGHT_SCHOLAR/
│
├── config/
│   ├── **init**.py
│   └── settings.py
│
├── core/
│   ├── **init**.py
│   ├── document_processing.py
│   ├── document_adapter.py
│   ├── embedding.py
│   ├── structure.py
│   └── vector_store.py
│
├── data/
├── utils/
│
├── attention_all_you_need.pdf
├── demo1.py
├── main.py
├── README.md
├── requirements.txt
├── pyproject.toml
└── uv.lock

```

---

## File Overview

### `core/document_processing.py`
- Loads PDF / text documents
- Converts documents to raw text
- Extracts section-level structure (Abstract, Introduction, Methodology, etc.)
- Builds a unified `ResearchPaper` object
- Generates section-aware text chunks with metadata

---

### `core/structure.py`
- Defines Pydantic data models:
  - `PaperSection`
  - `ResearchPaper`
- Acts as the canonical schema for research papers

---

### `core/document_adapter.py`
- Converts internal chunk representations into LangChain `Document` objects
- Acts as an adapter between preprocessing and vector indexing layers

---

### `core/embedding.py`
- Manages embedding model initialization
- Generates embeddings for text, multiple texts, or chunks
- Exposes embedding dimension and embedding interface

---

### `core/vector_store.py`
- Manages FAISS vector store lifecycle
- Creates vector store from LangChain documents
- Supports adding documents, searching, saving, loading, and retrievers

---

### `config/settings.py`
- Centralized configuration (embedding model name, top-k values, paths)

---

### `demo1.py`
- Demonstrates document processing, chunking, and semantic search
- Used for testing and debugging the pipeline

---

### `main.py`
- Entry point for running the end-to-end pipeline

---

## Current Capabilities

As of now, the system can:

- Ingest research papers in PDF format
- Remove document-level noise and extract clean text
- Identify and extract logical paper sections
- Build a structured `ResearchPaper` representation
- Chunk sections into semantically meaningful units
- Generate embeddings for chunks
- Index chunks using FAISS
- Perform semantic similarity search with top-k retrieval
- Persist and reload vector stores from disk

---

## Design Principles

- Section-aware processing for academic correctness
- Clear separation of concerns across modules
- Adapter-based integration with LangChain
- Production-style modular architecture

---

## Status

This project currently implements:
- Paper ingestion
- Structuring
- Chunking
- Embedding
- Vector search and retrieval

Further layers (UI, analytics, RAG answering) can be added on top of the existing foundation.

---

If you want next, I can:

* Tighten this for **academic submission**
* Convert it into **resume/project description**
* Add **architecture diagram**
* Add **usage instructions**

Just tell me 👍
