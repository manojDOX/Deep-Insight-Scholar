# Deep Insight Scholar 📘

Name - Manoj B

Mail ID - manoj2882003@gmail.com

Video Link -  **[Video Explanation](https://drive.google.com/file/d/1ZMiQwh6aN8qnxCeYTdJBqL88diFC5e1z/view?usp=sharing)**

**Deep Insight Scholar** is a modular research paper processing and semantic search intelligence system. It ingests academic PDF documents, extracts structured insights, and provides a powerful RAG (Retrieval-Augmented Generation) interface for researchers to query, analyze, and visualize trends across their document library.

🔗 **[Live Demo](https://deep-insight-scholar.streamlit.app/)**

---

## 🏗️ System Architecture

The system is designed with modular components and clear separation of concerns. The core pipeline transforms raw unstructured PDFs into a queryable knowledge base through four distinct stages:

1. **Document Processing** — Handles raw PDF loading, text extraction, and document-level noise reduction to ensure clean input data
2. **Structuring** — Parses logical sections of research papers (e.g., Abstract, Methodology, Conclusion) and synthesizes them into a unified `ResearchPaper` object
3. **Chunking** — Segments specific sections into semantically meaningful text units, preserving context for better retrieval
4. **Embedding & Indexing** — Generates vector embeddings for these chunks using high-performance models and indexes them in a FAISS vector store for sub-millisecond similarity search

The system utilizes adapter-based integration with LangChain to bridge internal data structures with advanced LLM capabilities.

---

## ✨ Key Features

- **Intelligent RAG Chat** — Chat with your documents using context-aware LLMs (Groq)
- **Hybrid Search** — Combines local document retrieval with Tavily web search for up-to-date context
- **Trend Analysis** — Visualize keyword frequency over time and detect emerging research topics
- **Citation/Influence Proxy** — Analyze paper influence based on keyword reuse and venue prestige

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd deep-insight-scholar
```

### 2. Create a Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
GPT_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=
TEMPRATURE=0
FAISS_INDEX_PATH=/data/faiss_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1300
CHUNK_OVERLAP=300
TOP_K_RESULTS=5
TAVILY_API_KEY=
METADATA_FILE=data/metadata/metadata.json
```

---

## ⚙️ Usage Instructions

This system operates in two modes: **Backend Ingestion** and **Frontend Visualization**.

### Step 1: Backend Data Ingestion

Before using the web interface, you must process your raw PDFs. This runs as a backend operation to ensure the FAISS index and metadata are pre-computed.

1. Place your PDF files into the `data/raw_pdf/` directory
2. Run the preparation script:

**macOS / Linux:**
```bash
python -m scripts.prepare_pdf
```

**Windows:**
```bash
python -m scripts.prepare_pdf
```

> **Note:** This process extracts metadata, chunks text, generates embeddings, and saves the `faiss_index` and `metadata.json` to disk.

### Step 2: Launch the Application

Once the data is processed, launch the Streamlit dashboard:

```bash
streamlit run main.py
```

The application will open in your browser at `http://localhost:8501`

Or visit the **[Live Demo](https://deep-insight-scholar.streamlit.app/)** to try it online.

---

## 📂 Project Structure

```
├── config/             # Configuration settings
├── core/               # Core logic (Chunking, Embedding, Vector Store)
├── data/               # Data storage (Raw PDFs, FAISS index, Metadata)
├── scripts/            # Backend scripts (prepare_pdf.py)
├── services/           # Business logic services
├── tools/              # External tools (Tavily Search)
├── ui/                 # Streamlit UI components and pages
├── utils/              # Helper utilities
└── main.py             # Application entry point
```

---

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 🤝 Support

For questions or issues, please open an issue on the repository.
