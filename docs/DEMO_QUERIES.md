# Demo Queries

Use these questions after adding and indexing the assignment documents in `data/`.

The exact source filenames may differ in your local folder. The "likely source" column names the kind of document that should be retrieved.

| # | Demo question | Expected answer theme | Likely source document |
|---|---|---|---|
| 1 | What does the Claude Code document say about agentic coding workflows? | Claude Code supports structured coding workflows where an agent can inspect, edit, and verify code with developer guidance. | Claude Code document |
| 2 | Which edge cases should an AI project handle before submission? | The project should handle missing inputs, unsupported files, empty retrieval results, provider errors, and unclear user questions. | AI project edge cases document |
| 3 | What are the key differences between the Perplexity models described in the documents? | The answer should compare model capabilities, use cases, or tradeoffs described in the Perplexity model notes. | Perplexity models document |
| 4 | How does the hybrid market research workflow combine manual and AI steps? | The workflow likely combines human research planning, AI-assisted summarization, source comparison, and final human validation. | Hybrid market research workflow document |
| 5 | What document processing or PDF skills are described? | The answer should mention extracting text, handling PDFs, preserving metadata, chunking documents, or validating source pages. | Document processing or PDF skills document |
| 6 | What does the collection say about cooking pasta for a restaurant menu? | This should be unanswerable unless the documents discuss cooking. The bot should say the provided documents do not contain enough information. | No relevant source expected |

## Screen Recording Tip

Ask at least two answerable questions and one unanswerable question. Show that the CLI displays:

- Final grounded answer
- Sources used
- Retrieved chunks
- Refusal behavior for unsupported questions

