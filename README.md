# RAG Document Q&A Bot

## Project Description

A Python 3.11+ Retrieval-Augmented Generation Document Q&A Bot for asking natural language questions against 4 to 5 local documents. The CLI loads local files, chunks their text, indexes embeddings into a persisted ChromaDB database, retrieves relevant chunks for a question, and generates grounded answers with source citations.

The bot is designed for an AI internship assignment and intentionally keeps indexing, retrieval, and answer generation separated.

## Tech Stack

- Python 3.11+
- PyMuPDF for PDF text extraction
- python-docx for DOCX loading
- python-dotenv for `.env` configuration
- sentence-transformers for local embeddings
- ChromaDB for persisted vector storage
- Rich for cleaner CLI output
- Groq SDK, Google Gen AI SDK (`google-genai`), or OpenAI SDK for LLM answer generation

## Architecture Overview

```text
data/ documents
  -> document loaders
  -> clean text with metadata
  -> overlapping chunks
  -> batched sentence-transformers embeddings
  -> persisted ChromaDB vector database
  -> query embedding
  -> top-k similarity search
  -> grounded LLM prompt
  -> cited final answer
```

Main entry points:

- `python index.py` builds or rebuilds the vector database.
- `python query.py` starts the interactive CLI.

## Supported Document Formats

- PDF, required by the assignment
- TXT
- DOCX

At least one PDF must be present in `data/` before indexing.

## Chunking Strategy

Text is split into fixed-size overlapping chunks.

Defaults:

- `CHUNK_SIZE=1000`
- `CHUNK_OVERLAP=200`

This keeps chunks large enough to preserve useful context while keeping retrieval focused. The overlap reduces the chance that important information is split across chunk boundaries.

## Embeddings and Vector Database

Default embedding model:

- `sentence-transformers/all-MiniLM-L6-v2`

This model is small, fast, local, and practical for a demo RAG system. Embeddings are created in batches during indexing, not one chunk at a time.

Vector database:

- ChromaDB
- Default path: `vector_db/`
- Default collection: `document_chunks`

ChromaDB is used because it persists locally and stores chunk text, vectors, and metadata together. You do not need to re-index every run unless documents or chunk settings change.

## Setup Instructions

1. Create and activate a Python 3.11+ virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.

```bash
copy .env.example .env
```

4. Configure one LLM provider in `.env`.

For Groq:

```text
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

For Gemini:

```text
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-2.0-flash
```

For OpenAI:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
```

5. Add 4 to 5 meaningful documents to `data/`.

6. Run indexing.

```bash
python index.py
```

7. Start the CLI.

```bash
python query.py
```

## Groq Setup

Groq can be used to generate final grounded answers when Gemini quota is unavailable.

1. Create a Groq API key from GroqCloud.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set `.env`:

```text
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

4. Run:

```bash
python query.py
```

Groq is used only for answer generation. Embeddings still use sentence-transformers locally, and vector search still uses ChromaDB. If Groq model access fails, try another supported Groq chat model available in the Groq console.

## Environment Variables

- `LLM_PROVIDER`: `groq`, `gemini`, or `openai`
- `GROQ_API_KEY`: required when `LLM_PROVIDER=groq`
- `GROQ_MODEL`: Groq chat model name, default `openai/gpt-oss-120b`
- `GOOGLE_API_KEY`: required when `LLM_PROVIDER=gemini`
- `OPENAI_API_KEY`: required when `LLM_PROVIDER=openai`
- `LLM_MODEL`: Gemini or OpenAI model name
- `EMBEDDING_PROVIDER`: currently `sentence-transformers`
- `EMBEDDING_MODEL`: embedding model name
- `EMBEDDING_BATCH_SIZE`: document embedding batch size
- `DATA_DIR`: document folder, default `data`
- `CHROMA_PERSIST_DIR`: vector database folder, default `vector_db`
- `CHROMA_COLLECTION_NAME`: default `document_chunks`
- `CHUNK_SIZE`: default `1000`
- `CHUNK_OVERLAP`: default `200`
- `TOP_K`: number of chunks retrieved per question, default `5`

## Quick Verification

Run indexing:

```bash
python index.py
```

Expected indexing output includes:

- Files found
- Document pages/sections extracted
- Chunks created
- Embedding model
- Vector database path
- Collection name
- Vectors stored

Run the CLI:

```bash
python query.py
```

Expected query output includes:

- User question
- Final grounded answer
- Sources used
- Retrieved chunks

## Example Queries

See `docs/DEMO_QUERIES.md` for demo-ready questions.

Examples:

- "What does the Claude Code document say about agentic coding workflows?"
- "Which edge cases should an AI project handle?"
- "What are the key differences between the Perplexity models?"
- "How does the hybrid market research workflow combine manual and AI steps?"
- "What document processing or PDF extraction skills are described?"
- "What does the document collection say about cooking pasta?"

## Grounded Answering Behavior

The LLM prompt requires answers to use only retrieved context. If the retrieved chunks do not contain the answer, the bot must say:

```text
The provided documents do not contain enough information to answer this question.
```

Answers include inline citations in this format:

```text
[source: filename, page/section: number, chunk: index]
```

The CLI displays deduplicated sources from retrieved chunk metadata, independent of whether the LLM includes citations in its wording. It also displays the detailed retrieved chunks so the retrieval step can be inspected.

## What To Show In A Screen Recording

1. Show the `data/` folder with 4 to 5 documents and at least one PDF.
2. Show `.env` with API key values hidden.
3. Run `python index.py`.
4. Point out files found, chunks created, embedding model, and vectors stored.
5. Run `python query.py`.
6. Ask one answerable question and show the final cited answer.
7. Show the sources used and retrieved chunks.
8. Ask one unanswerable question and show the refusal behavior.

## Troubleshooting

Missing API key:

- Groq requires `GROQ_API_KEY`.
- Gemini requires `GOOGLE_API_KEY`.
- OpenAI requires `OPENAI_API_KEY`.
- Add the correct key to `.env` and rerun `python query.py`.

If `query.py` still shows Gemini after setting Groq:

- Ensure you edited `.env`, not `.env.example`.
- Run:

```bash
python query.py --show-config
```

- Check that `LLM_PROVIDER` is `groq`.
- Check that `Active model` is `openai/gpt-oss-120b`.
- Restart the terminal if old shell variables were set.
- Remove stale shell variables if needed in PowerShell:

```powershell
Remove-Item Env:LLM_PROVIDER
Remove-Item Env:LLM_MODEL
```

- Never commit `.env`.

No indexed documents:

- Run `python index.py` before `python query.py`.
- Make sure `data/` contains documents and at least one PDF.

`sentence-transformers` missing:

- Run `pip install -r requirements.txt`.
- Confirm your virtual environment is active.

Hugging Face warning:

- Some sentence-transformers models may show cache or download warnings on first run.
- This is usually normal as long as the model loads successfully.

Windows symlink warning:

- Hugging Face may warn that symlinks are unavailable on Windows.
- The warning is usually safe to ignore; model caching may use more disk space.

Gemini quota exceeded or 429 error:

- Wait for quota reset, try `gemini-2.5-flash`, switch to another valid model, or configure OpenAI instead.
- Retrieval output is still useful for verifying that the RAG pipeline found relevant chunks.

Groq model access error:

- Confirm `GROQ_API_KEY` is set in `.env`.
- Confirm `GROQ_MODEL` is available in your Groq console.
- Try another supported Groq chat model if access fails.

Deprecated Gemini package warning:

- The Gemini provider uses `google-genai`, not the deprecated `google-generativeai` package.
- If you see a deprecated `google.generativeai` warning, reinstall dependencies after migration:

```bash
pip install -r requirements.txt
```

ChromaDB import error:

- Run `pip install -r requirements.txt`.
- Confirm the same environment is used for indexing and querying.

## Known Limitations

- The CLI depends on retrieved context quality.
- The LLM can only cite chunks retrieved by the vector search.
- Scanned PDFs without selectable text may need OCR, which is not implemented.
- Streamlit UI is intentionally not implemented yet.
- The project is a basic assignment implementation, not a production RAG system.

## Project Structure

```text
rag-document-qa-bot/
├── data/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_QUERIES.md
│   └── TASKS.md
├── src/
│   ├── loaders/
│   ├── chunking/
│   ├── embeddings/
│   ├── vectorstore/
│   ├── retrieval/
│   ├── generation/
│   └── utils/
├── vector_db/
├── index.py
├── query.py
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── AGENTS.md
```
