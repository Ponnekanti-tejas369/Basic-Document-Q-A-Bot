# AGENTS.md

## Project Mission

Build a Python 3.11+ Retrieval-Augmented Generation Document Q&A Bot for an AI internship assignment.

The bot will let a user ask natural language questions against 4 to 5 meaningful local documents stored in `data/`, then return grounded answers with source citations.

## Current Phase

Core CLI RAG pipeline is polished and supports Gemini, OpenAI, and Groq LLM providers:

- Document loading for PDF, TXT, and DOCX files.
- Text normalization.
- Metadata preservation.
- Fixed-size overlapping chunking.
- sentence-transformers embedding layer.
- Batched chunk embeddings.
- ChromaDB persisted vector store.
- `index.py` performs real indexing.
- Similarity search over ChromaDB.
- Retriever module.
- `query.py` interactive CLI.
- Source chunk citation display.
- Grounded LLM answer generation.
- Gemini/OpenAI/Groq provider abstraction.
- `query.py` now retrieves chunks and generates cited answers.
- Project-root `.env` loading is centralized in `src/utils/config.py`.
- Gemini provider uses the `google-genai` SDK, not deprecated `google-generativeai`.
- Final CLI output shows the user question, grounded answer, deduplicated sources, and retrieved chunks.
- README and demo query documentation are assessment-ready.

Do not implement Streamlit UI unless explicitly requested.

## Development Rules

- Use Python 3.11 or higher.
- Keep indexing and querying as separate flows.
- Keep code modular under `src/`.
- Do not hardcode API keys or secrets.
- Read configuration from `.env`.
- Persist the vector database under `vector_db/`.
- Store chunk metadata, including source filename and page number or section.
- Embed chunks in batches.
- Generate answers only from retrieved context.
- Always include citations in generated answers.
- If retrieved context is insufficient, say the documents do not contain enough information.

## Planned Project Structure

```text
rag-document-qa-bot/
├── data/
├── docs/
│   ├── ARCHITECTURE.md
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

## Documentation Maintenance

Update `docs/TASKS.md` after every major implementation step.
