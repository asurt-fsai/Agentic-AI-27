from __future__ import annotations

from pathlib import Path
from typing import Protocol

from fsai_agents.core.memory.models import SourceRecord
from fsai_agents.core.policy.sensitivity import enforce_cloud_parser_policy


class DocumentParser(Protocol):
    """Protocol implemented by local and gated cloud document parsers."""

    def parse(self, path: Path, source: SourceRecord) -> str: ...


class LocalTextParser:
    """Native UTF-8 reader for Markdown, Python, and plain-text files."""

    def parse(self, path: Path, source: SourceRecord) -> str:
        return path.read_text(encoding="utf-8")


class DoclingParser:
    """Local-first Docling parser for PDFs and structured office documents."""

    def parse(self, path: Path, source: SourceRecord) -> str:
        try:
            from docling.document_converter import DocumentConverter
        except ImportError as exc:
            raise RuntimeError(
                "Docling is not installed. Install optional dependencies with "
                '`pip install -e ".[ingestion]"`.'
            ) from exc

        converter = DocumentConverter()
        result = converter.convert(str(path))
        return result.document.export_to_markdown()


class LlamaParseAdapter:
    """Cloud parser adapter hard-gated to 'api-ok' sources only."""

    def parse(self, path: Path, source: SourceRecord) -> str:
        enforce_cloud_parser_policy(source.sensitivity, source.source_id)
        try:
            from llama_parse import LlamaParse
        except ImportError as exc:
            raise RuntimeError(
                "llama-parse is not installed. Install optional dependencies with "
                '`pip install -e ".[ingestion]"`.'
            ) from exc

        parser = LlamaParse(result_type="markdown")
        docs = parser.load_data(str(path))
        return "\n\n".join(getattr(doc, "text", str(doc)) for doc in docs)


def select_parser(path: Path, source: SourceRecord) -> DocumentParser:
    """Select parser per T18 policy: Docling/local by default, LlamaParse only if api-ok."""
    if path.suffix.lower() in {".md", ".markdown", ".py", ".txt"}:
        return LocalTextParser()
    if source.parser == "llamaparse":
        enforce_cloud_parser_policy(source.sensitivity, source.source_id)
        return LlamaParseAdapter()
    if source.parser == "docling" or path.suffix.lower() in {".pdf", ".docx"}:
        return DoclingParser()
    return LocalTextParser()
