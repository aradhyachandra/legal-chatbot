# ⚖️ Legal RAG Chatbot

A fully local, privacy-first **Retrieval-Augmented Generation (RAG)** chatbot for Indian legal documents. Ask natural language questions about any indexed PDF — the system retrieves the most relevant passages and generates a grounded answer using a local LLM, with **zero data leaving your machine**.

---

## 🏗️ Architecture Overview

```
PDF Documents (data/raw/)
        │
        ▼
  [ Document Loader ]         ← pypdf  (src/ingestion/load_docs.py)
        │
        ▼
  [ Text Chunker ]            ← LangChain RecursiveCharacterTextSplitter (src/ingestion/chunk_docs.py)
        │
        ▼
  [ Embedding Model ]         ← nomic-embed-text via Ollama (src/retrieval/create_embeddings.py)
        │
        ▼
  [ Vector Store ]            ← ChromaDB persistent store (embeddings/chroma_db/)
        │
   Query time:
        │
        ▼
  [ Query Embedder ]          ← same nomic-embed-text model
        │
        ▼
  [ Similarity Search ]       ← top-3 chunks, distance threshold ≤ 0.65
        │
        ▼
  [ LLM (llama3.2) ]          ← strictly grounded prompt via Ollama (src/rag/rag_pipeline.py)
        │
        ▼
  [ Streamlit UI ]            ← chat interface with context transparency (src/ui/app.py)
```

---

## ✨ Features

- **100% Local** — runs entirely on your machine via [Ollama](https://ollama.com); no API keys, no cloud.
- **Strictly Grounded Answers** — the LLM is prompted to answer **only** from retrieved context; if the answer isn't in the documents, it says so.
- **Distance-Filtered Retrieval** — chunks with a cosine distance > 0.65 are automatically discarded to prevent irrelevant context from leaking into answers.
- **Transparent Context** — every assistant response includes an expandable panel showing the exact retrieved chunks and their distance scores.
- **Hallucination Disclaimer** — a visible reminder is shown under every answer to always verify with a qualified legal professional.
- **Persistent Vector Store** — embeddings are stored in ChromaDB and survive restarts; re-indexing only needed when documents change.
- **Multi-document Support** — drop any number of PDFs into `data/raw/` and re-run the ingestion pipeline.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | `llama3.2` (via Ollama) |
| Embedding Model | `nomic-embed-text` (via Ollama) |
| Vector Database | ChromaDB (persistent, local) |
| PDF Parsing | pypdf |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` |
| RAG Orchestration | LangChain + LangChain-Ollama |
| UI | Streamlit |
| Language | Python 3.11+ |

---

## 📁 Project Structure

```
legal-chatbot/
├── data/
│   └── raw/                        # Place your PDF documents here
│       └── indian_contract_act_sample.pdf
├── embeddings/
│   └── chroma_db/                  # Auto-generated persistent vector store
├── src/
│   ├── ingestion/
│   │   ├── load_docs.py            # Loads PDFs from data/raw/ into LangChain Documents
│   │   └── chunk_docs.py           # Splits documents into 500-token chunks (50 token overlap)
│   ├── retrieval/
│   │   ├── create_embeddings.py    # Generates embeddings and stores them in ChromaDB
│   │   └── query_vectors.py        # CLI tool for testing vector retrieval
│   ├── rag/
│   │   ├── rag_pipeline.py         # Core RAG logic: embed query → retrieve → prompt → LLM
│   │   └── test_ollama.py          # Sanity check for Ollama connectivity
│   └── ui/
│       └── app.py                  # Streamlit chat application
├── config/
│   └── settings.yaml               # (Reserved for future configuration)
├── tests/
│   └── generate_dummy_pdf.py       # Helper to generate test PDF fixtures
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.11+**
2. **[Ollama](https://ollama.com)** installed and running locally.
3. Pull the required models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd legal-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 📖 Usage

Follow these steps **in order** every time you add new documents. If your documents haven't changed, jump straight to Step 2.

### Step 1 — Add Documents & Generate Embeddings

Place one or more PDF files in `data/raw/`, then run:

```bash
python -m src.retrieval.create_embeddings
```

This will:
- Load all PDFs from `data/raw/`
- Split them into 500-character chunks with 50-character overlap
- Embed each chunk using `nomic-embed-text`
- Store all vectors in `embeddings/chroma_db/` (existing collection is replaced to prevent duplicates)

### Step 2 — Launch the Chatbot UI

```bash
streamlit run src/ui/app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔍 How RAG Works (Under the Hood)

1. **Query** — the user's question is embedded using `nomic-embed-text`.
2. **Retrieve** — ChromaDB performs a vector similarity search and returns the top 3 chunks.
3. **Filter** — chunks with a cosine distance score above `0.65` are discarded (too dissimilar to be useful).
4. **Prompt** — the remaining chunks are injected into a strict, grounded prompt that instructs `llama3.2` not to use any outside knowledge.
5. **Generate** — the LLM produces a response grounded exclusively in the retrieved context.
6. **Fallback** — if no chunks survive the distance filter, the system returns a standard "insufficient information" message rather than hallucinating.

---

## 🧪 Testing & Debugging

**Test Ollama connectivity:**
```bash
python -m src.rag.test_ollama
```

**Test vector retrieval directly (CLI):**
```bash
python -m src.retrieval.query_vectors
```
This runs a hard-coded test query and prints the top 3 retrieved chunks with their distance scores and metadata.

**Run the full RAG pipeline (CLI, no UI):**
```bash
python -m src.rag.rag_pipeline
```
Runs three test queries — two in-context and one out-of-context — to validate end-to-end behavior.

---

## ⚙️ Configuration

Key parameters are currently defined as constants in the source files. Future versions will centralise these in `config/settings.yaml`.

| Parameter | Default | Location |
|---|---|---|
| `chunk_size` | `500` | `src/ingestion/chunk_docs.py` |
| `chunk_overlap` | `50` | `src/ingestion/chunk_docs.py` |
| `n_results` (top-k) | `3` | `src/rag/rag_pipeline.py` |
| `distance_threshold` | `0.65` | `src/rag/rag_pipeline.py` |
| `llm_model` | `llama3.2` | `src/rag/rag_pipeline.py` |
| `embedding_model` | `nomic-embed-text` | `src/retrieval/create_embeddings.py` |
| `chroma_path` | `./embeddings/chroma_db` | `src/retrieval/create_embeddings.py` |

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. Answers are grounded in the indexed documents and may be incomplete or inaccurate. **Always consult a qualified legal professional** for actual legal advice.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
