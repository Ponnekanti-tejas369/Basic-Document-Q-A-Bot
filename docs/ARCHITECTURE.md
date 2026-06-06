# Architecture

## Overview

This project will implement a basic Retrieval-Augmented Generation pipeline for local document question answering.

The system will index 4 to 5 local documents from `data/`, persist their embeddings in a local vector database, and provide a command-line interface for grounded Q&A with source citations.

## Core Components

### Document Loading

Planned location: `src/loaders/`

Responsibilities:

- Load documents from `data/`.
- Support PDF as a required format.
- Optionally support TXT and DOCX.
- Extract clean text.
- Preserve metadata such as source filename and page number or section.

### Chunking

Planned location: `src/chunking/`

Responsibilities:

- Split extracted text into overlapping chunks.
- Keep chunks large enough for context and small enough for retrieval precision.
- Attach document metadata to every chunk.

### Embeddings

Planned location: `src/embeddings/`

Responsibilities:

- Convert chunks and user questions into vectors.
- Batch embedding calls for indexing.
- Avoid one-chunk-at-a-time embedding during ingestion.

### Vector Store

Planned location: `src/vectorstore/`

Responsibilities:

- Store chunk embeddings and metadata.
- Use a persisted local vector database such as ChromaDB.
- Keep indexed data under `vector_db/`.

### Retrieval

Planned location: `src/retrieval/`

Responsibilities:

- Embed a user question.
- Retrieve the top-k most relevant chunks.
- Return chunk text and metadata for answer generation.

### Generation

Planned location: `src/generation/`

Responsibilities:

- Call an LLM using environment-based API configuration.
- Generate answers only from retrieved context.
- Include source citations.
- Refuse unsupported answers when context is insufficient.

### CLI

Planned files:

- `index.py`: indexing entry point.
- `query.py`: interactive question-answering CLI.
- `app.py`: optional Streamlit UI placeholder for a later phase.

## Planned Data Flow

```text
data documents
  -> document loader
  -> clean text with metadata
  -> chunker with overlap
  -> batched embedding model
  -> persisted vector database
  -> user question
  -> question embedding
  -> top-k retrieval
  -> grounded LLM answer
  -> answer with citations
```

## Configuration

Configuration will be loaded from `.env` using `python-dotenv`.

Planned configurable values include:

- API provider and API key.
- Embedding model.
- LLM model.
- ChromaDB persistence path.
- Collection name.
- Chunk size.
- Chunk overlap.
- Retrieval `top_k`.

## Initial Technology Choices

- Python 3.11+
- ChromaDB for persisted vector storage.
- PyMuPDF for PDF text extraction.
- python-docx for optional DOCX support.
- sentence-transformers for local embeddings.
- Google Gemini API or OpenAI API for answer generation.
- Rich or simple standard input loop for CLI.

