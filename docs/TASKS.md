# Tasks

## Phase 0: Project Scaffold

- [x] Create initial project folders.
- [x] Create `AGENTS.md`.
- [x] Create `docs/ARCHITECTURE.md`.
- [x] Create `docs/TASKS.md`.
- [x] Create `README.md` skeleton.
- [x] Create `requirements.txt`.
- [x] Create `.env.example`.
- [x] Add placeholder files so empty folders are visible.

## Phase 1: Document Loading

- [x] Add PDF loader.
- [x] Add TXT loader.
- [x] Add DOCX loader.
- [x] Normalize extracted text.
- [x] Preserve source filename and page or section metadata.
- [x] Add loader error handling.

## Phase 2: Chunking

- [x] Implement overlapping text chunker.
- [x] Make chunk size and overlap configurable.
- [x] Attach metadata to every chunk.
- [x] Add basic chunk validation.
- [x] Add basic `index.py` loading and chunking test.

## Phase 3: Embeddings

- [x] Add embedding provider abstraction.
- [x] Implement local sentence-transformers embeddings.
- [x] Batch embedding calls during indexing.
- [x] Add embedding configuration through `.env`.

## Phase 4: Vector Store

- [x] Add ChromaDB integration.
- [x] Persist vector database to `vector_db/`.
- [x] Store chunk text, embeddings, and metadata.
- [x] Add collection reset or rebuild option.

## Phase 5: Indexing CLI

- [x] Implement `index.py`.
- [x] Load 4 to 5 documents from `data/`.
- [x] Validate that at least one PDF is present.
- [x] Print indexing summary.
- [x] Add ChromaDB similarity search.
- [x] Add query embedding path.
- [x] Add top-k retrieval.

## Phase 6: Query CLI

- [x] Implement `query.py`.
- [x] Add interactive question loop.
- [x] Embed user questions.
- [x] Retrieve top-k chunks.
- [x] Display retrieved source chunks and citations.
- [x] Make `top_k` configurable.
- [x] Add citation formatting helper.

## Phase 7: Answer Generation

- [x] Add LLM provider abstraction.
- [x] Add Gemini LLM support.
- [x] Add OpenAI LLM support.
- [x] Add Groq LLM provider.
- [x] Add `LLM_PROVIDER=groq` support.
- [x] Add `GROQ_API_KEY` configuration.
- [x] Add Groq answer generation from retrieved context.
- [x] Implement grounded prompt template.
- [x] Generate answers from retrieved context.
- [x] Refuse unsupported answers when retrieved context is insufficient.
- [x] Include citations in every answer.

## Phase 8: Optional UI

- [ ] Add Streamlit app only after CLI works.
- [ ] Keep CLI as the minimum working interface.

## Phase 9: Final Polish

- [x] Add centralized project-root `.env` config loader.
- [x] Add safe `query.py --show-config` diagnostics.
- [x] Migrate Gemini provider to `google-genai` SDK.
- [x] Add example documents or document guidance.
- [x] Add setup verification steps.
- [x] Add example questions.
- [x] Improve query output.
- [x] Add source deduplication.
- [x] Add demo query guide.
- [x] Add README assignment checklist.
- [x] Add `.gitignore`.
- [x] Add troubleshooting docs.
- [x] Document known limitations.
- [x] Run compile and no-API verification.
