"""Interactive RAG query CLI with grounded answer generation."""

from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path

from src.embeddings import create_embedder
from src.generation import (
    INSUFFICIENT_CONTEXT_RESPONSE,
    build_grounded_prompt,
    create_llm,
)
from src.retrieval import Retriever
from src.utils import format_citation
from src.utils.config import (
    get_active_llm_model,
    get_env,
    get_env_path,
    get_llm_model_label,
    get_llm_provider,
    get_project_root,
    get_raw_env_value,
    has_env_value,
    load_project_env,
)
from src.vectorstore import ChromaStore

NO_INDEX_MESSAGE = (
    "No indexed documents found. Please add documents to data/ and run "
    "python index.py first."
)
EXIT_COMMANDS = {"exit", "quit", "q"}
NO_RELEVANT_CHUNKS_MESSAGE = "No relevant chunks were found for this question."
NO_SOURCES_MESSAGE = "No sources available."


def read_top_k() -> int:
    value = get_env("TOP_K", "5")
    try:
        top_k = int(value)
    except ValueError as exc:
        raise ValueError("TOP_K must be an integer.") from exc

    if top_k <= 0:
        raise ValueError("TOP_K must be greater than 0.")

    return top_k


def get_llm_label() -> str:
    return get_llm_model_label()


def print_config_debug() -> None:
    env_path = get_env_path()
    print(f"Project root: {get_project_root()}")
    print(f"Env file: {env_path}")
    print(f"Env exists: {'yes' if env_path.exists() else 'no'}")
    print(f"Raw .env LLM_PROVIDER: {get_raw_env_value('LLM_PROVIDER') or '<missing>'}")
    print(f"Final os.environ LLM_PROVIDER: {os.environ.get('LLM_PROVIDER', '<missing>')}")
    print(f"get_llm_provider(): {get_llm_provider()}")
    print(f"Active model: {get_active_llm_model()}")
    print(f"GROQ_API_KEY present: {'yes' if has_env_value('GROQ_API_KEY') else 'no'}")
    print(f"GOOGLE_API_KEY present: {'yes' if has_env_value('GOOGLE_API_KEY') else 'no'}")
    print(f"OPENAI_API_KEY present: {'yes' if has_env_value('OPENAI_API_KEY') else 'no'}")


def has_persisted_index(persist_dir: str | Path) -> bool:
    path = Path(persist_dir)
    if not path.exists() or not path.is_dir():
        return False

    return any(child.is_file() and child.name != ".gitkeep" for child in path.rglob("*"))


def deduplicate_sources(results: list[object]) -> list[dict[str, object]]:
    seen: set[tuple[object, object, object]] = set()
    sources: list[dict[str, object]] = []

    for result in results:
        source_metadata = extract_source_info(result)
        key = (
            source_metadata.get("source", ""),
            source_metadata.get("page_number", ""),
            source_metadata.get("chunk_index", ""),
        )
        if key in seen:
            continue

        seen.add(key)
        sources.append(source_metadata)

    return sources


def extract_source_info(result: object) -> dict[str, object]:
    """Extract citation fields from dict, nested metadata, or object results."""

    metadata = _get_result_value(result, "metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    return {
        "source": _first_present(
            metadata.get("source"),
            metadata.get("filename"),
            metadata.get("source_filename"),
            _get_result_value(result, "source"),
            _get_result_value(result, "filename"),
            _get_result_value(result, "source_filename"),
            "unknown",
        ),
        "page_number": _first_present(
            metadata.get("page_number"),
            metadata.get("page"),
            metadata.get("section"),
            _get_result_value(result, "page_number"),
            _get_result_value(result, "page"),
            _get_result_value(result, "section"),
            "unknown",
        ),
        "chunk_index": _first_present(
            metadata.get("chunk_index"),
            metadata.get("chunk"),
            _get_result_value(result, "chunk_index"),
            _get_result_value(result, "chunk"),
            "unknown",
        ),
    }


def _get_result_value(result: object, key: str, default: object = None) -> object:
    if isinstance(result, dict):
        return result.get(key, default)

    return getattr(result, key, default)


def _first_present(*values: object) -> object:
    for value in values:
        if value not in (None, ""):
            return value

    return "unknown"


class QueryConsole:
    """Small output wrapper with Rich support when installed."""

    def __init__(self) -> None:
        try:
            from rich.console import Console
            from rich.markup import escape
            from rich.panel import Panel
        except ImportError:
            self.rich = False
            self.console = None
            self.panel = None
            self.escape = None
            return

        self.rich = True
        self.console = Console()
        self.panel = Panel
        self.escape = escape

    def print(self, message: str = "") -> None:
        if self.rich:
            self.console.print(message)
        else:
            print(message)

    def print_startup(self, top_k: int, vector_count: int, llm_model: str) -> None:
        message = (
            "RAG Query CLI ready. Questions are answered only from retrieved "
            "document chunks with citations."
        )
        if self.rich:
            self.console.print(self.panel(message, title="RAG Query CLI"))
            self.console.print(
                f"Indexed chunks: {vector_count} | top_k: {top_k} | LLM: {llm_model}"
            )
        else:
            print("RAG Query CLI")
            print(message)
            print(f"Indexed chunks: {vector_count} | top_k: {top_k} | LLM: {llm_model}")

    def print_answer(self, answer: str) -> None:
        if self.rich:
            self.console.print(self.panel(answer, title="Final Grounded Answer"))
        else:
            print("\nFinal Grounded Answer")
            print(answer)

    def print_question(self, question: str) -> None:
        if self.rich:
            self.console.print(self.panel(question, title="User Question"))
        else:
            print("\nUser Question")
            print(question)

    def print_sources(self, results: list[dict[str, object]]) -> None:
        sources = deduplicate_sources(results)
        source_lines = [format_citation(source) for source in sources]
        if self.rich:
            body = "\n".join(self.escape(line) for line in source_lines)
            self.console.print(self.panel(body or NO_SOURCES_MESSAGE, title="Sources Used"))
            return

        print("\nSources Used")
        if not sources:
            print(NO_SOURCES_MESSAGE)
            return

        for line in source_lines:
            print(f"- {line}")

    def print_results(self, results: list[dict[str, object]]) -> None:
        if self.rich:
            self.console.print("[bold]Retrieved Chunks[/bold]")
        else:
            print("\nRetrieved Chunks")

        if not results:
            self.print(NO_RELEVANT_CHUNKS_MESSAGE)
            return

        if self.rich:
            for rank, result in enumerate(results, start=1):
                metadata = result.get("metadata", {})
                citation = format_citation(metadata)
                preview = textwrap.shorten(
                    str(result.get("text", "")).replace("\n", " "),
                    width=500,
                )
                body = (
                    f"{citation}\n"
                    f"file type: {result.get('file_type', '')}\n"
                    f"file path: {result.get('file_path', '')}\n"
                    f"distance: {result.get('score')}\n\n"
                    f"{preview}"
                )
                self.console.print(self.panel(body, title=f"Result {rank}"))
            return

        for rank, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            preview = textwrap.shorten(
                str(result.get("text", "")).replace("\n", " "),
                width=500,
            )
            print(f"\nResult {rank}")
            print(f"  citation: {format_citation(metadata)}")
            print(f"  chunk_id: {result.get('chunk_id', '')}")
            print(f"  source: {result.get('source', '')}")
            print(f"  file_path: {result.get('file_path', '')}")
            print(f"  file_type: {result.get('file_type', '')}")
            print(f"  page_number: {result.get('page_number', '')}")
            print(f"  chunk_index: {result.get('chunk_index', '')}")
            print(f"  distance: {result.get('score')}")
            print(f"  preview: {preview}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the RAG document Q&A bot.")
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print safe environment configuration diagnostics and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_project_env()

    if args.show_config:
        print_config_debug()
        return

    console = QueryConsole()

    try:
        top_k = read_top_k()
        persist_dir = get_env("CHROMA_PERSIST_DIR", "vector_db")

        if not has_persisted_index(persist_dir):
            console.print(NO_INDEX_MESSAGE)
            return

        vector_store = ChromaStore(create_if_missing=False)
        vector_count = vector_store.count()
        if vector_count == 0:
            console.print(NO_INDEX_MESSAGE)
            return

        embedder = create_embedder()
        retriever = Retriever(embedder=embedder, vector_store=vector_store, top_k=top_k)
        llm_label = get_llm_label()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc

    console.print_startup(top_k=top_k, vector_count=vector_count, llm_model=llm_label)
    console.print("Type exit, quit, or q to stop.")

    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in EXIT_COMMANDS:
            console.print("Goodbye.")
            break

        if not question:
            console.print("Please enter a question or type exit to stop.")
            continue

        try:
            results = retriever.retrieve(question)
            console.print_question(question)

            if not results:
                console.print_answer(INSUFFICIENT_CONTEXT_RESPONSE)
                console.print_sources(results)
                console.print_results(results)
                continue

            prompt = build_grounded_prompt(question, results)
            try:
                llm = create_llm()
                answer = llm.generate(prompt).strip()
            except Exception as exc:
                answer = f"LLM answer generation failed: {exc}"

            if not answer:
                answer = INSUFFICIENT_CONTEXT_RESPONSE

            console.print_answer(answer)
            console.print_sources(results)
            console.print_results(results)
        except Exception as exc:
            console.print(f"Error: {exc}")
            continue


if __name__ == "__main__":
    main()
