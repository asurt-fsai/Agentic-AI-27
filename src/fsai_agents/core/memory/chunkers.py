from __future__ import annotations

import ast
import hashlib
import re

from fsai_agents.core.memory.models import ChunkMetadata, DocumentChunk, SourceRecord

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CLAUSE_RE = re.compile(r"^(?:#{1,6}\s+)?([A-Z]{1,3}\d+(?:\.\d+){1,3})\b(.*)$")


def _make_chunk_id(source_id: str, file_path: str, index: int, text: str) -> str:
    digest = hashlib.sha256(f"{source_id}:{file_path}:{index}:{text}".encode()).hexdigest()[:16]
    return f"{source_id}::{digest}"


def _build_metadata(
    source: SourceRecord,
    file_path: str,
    *,
    heading_path: str = "",
    symbol: str = "",
    clause_id: str = "",
) -> ChunkMetadata:
    return ChunkMetadata(
        source_id=source.source_id,
        source_type=source.source_type,
        sensitivity=source.sensitivity.value,
        acl=source.acl.value,
        namespace=source.namespace,
        file_path=file_path,
        title=source.title,
        edition=source.edition,
        heading_path=heading_path,
        symbol=symbol,
        clause_id=clause_id,
    )


def _split_markdown_blocks(text: str) -> list[tuple[str, str]]:
    """Split markdown into (heading_path, section_body) keeping fences & tables intact."""
    sections: list[tuple[str, str]] = []
    heading_stack: list[tuple[int, str]] = []
    buffer: list[str] = []
    in_fence = False

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if body:
            path = " > ".join(h for _, h in heading_stack) or "Document"
            sections.append((path, body))
        buffer.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            buffer.append(line)
            continue

        if not in_fence:
            match = HEADING_RE.match(line)
            if match:
                flush()
                level = len(match.group(1))
                title = match.group(2).strip()
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, title))
                buffer.append(line)
                continue

        buffer.append(line)

    flush()
    return sections


def chunk_markdown(
    text: str,
    source: SourceRecord,
    file_path: str,
) -> list[DocumentChunk]:
    """Chunk markdown/Notion docs by heading while preserving tables and code blocks."""
    chunks: list[DocumentChunk] = []
    for idx, (heading_path, body) in enumerate(_split_markdown_blocks(text)):
        situated = f"[{source.title} | {heading_path}]\n{body}"
        chunks.append(
            DocumentChunk(
                chunk_id=_make_chunk_id(source.source_id, file_path, idx, situated),
                text=situated,
                metadata=_build_metadata(source, file_path, heading_path=heading_path),
            )
        )
    return chunks


def chunk_rulebook(
    text: str,
    source: SourceRecord,
    file_path: str,
) -> list[DocumentChunk]:
    """Chunk FS-AI rulebook text by clause/rule ID (e.g. IN2.2.2, D1.3.1, T4.5.1)."""
    chunks: list[DocumentChunk] = []
    current_clause = ""
    current_lines: list[str] = []
    in_fence = False

    def flush(idx: int) -> None:
        body = "\n".join(current_lines).strip()
        if not body:
            return
        label = current_clause or "Frontmatter"
        edition = source.edition or "unknown"
        situated = f"[{source.title} ({edition}) | {label}]\n{body}"
        chunks.append(
            DocumentChunk(
                chunk_id=_make_chunk_id(source.source_id, file_path, idx, situated),
                text=situated,
                metadata=_build_metadata(
                    source,
                    file_path,
                    heading_path=label,
                    clause_id=current_clause,
                ),
            )
        )

    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            current_lines.append(line)
            continue

        if not in_fence:
            match = CLAUSE_RE.match(line.strip())
            if match:
                flush(len(chunks))
                current_clause = match.group(1)
                current_lines = [line]
                continue

        current_lines.append(line)

    flush(len(chunks))
    return chunks


def chunk_python_ast(
    text: str,
    source: SourceRecord,
    file_path: str,
) -> list[DocumentChunk]:
    """Chunk Python code by top-level function/class AST nodes (cAST pattern)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_plain_text(text, source, file_path)

    lines = text.splitlines()
    chunks: list[DocumentChunk] = []
    covered_lines: set[int] = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = getattr(node, "lineno", 1) - 1
            end = getattr(node, "end_lineno", start + 1)
            covered_lines.update(range(start, end))
            snippet = "\n".join(lines[start:end]).strip()
            if not snippet:
                continue
            situated = f"[{source.source_id} | {file_path} | {node.name}]\n{snippet}"
            chunks.append(
                DocumentChunk(
                    chunk_id=_make_chunk_id(source.source_id, file_path, len(chunks), situated),
                    text=situated,
                    metadata=_build_metadata(source, file_path, symbol=node.name),
                )
            )

    if not chunks:
        return chunk_plain_text(text, source, file_path)

    module_lines = [line for i, line in enumerate(lines) if i not in covered_lines]
    module_preamble = "\n".join(module_lines).strip()
    if module_preamble:
        situated = f"[{source.source_id} | {file_path} | <module>]\n{module_preamble}"
        chunks.insert(
            0,
            DocumentChunk(
                chunk_id=_make_chunk_id(source.source_id, file_path, 9999, situated),
                text=situated,
                metadata=_build_metadata(source, file_path, symbol="<module>"),
            ),
        )

    return chunks


def chunk_plain_text(
    text: str,
    source: SourceRecord,
    file_path: str,
    max_lines: int = 80,
) -> list[DocumentChunk]:
    """Fallback bounded line chunker for non-markdown, non-Python files."""
    lines = text.splitlines()
    chunks: list[DocumentChunk] = []
    for start in range(0, len(lines), max_lines):
        block = "\n".join(lines[start : start + max_lines]).strip()
        if not block:
            continue
        situated = f"[{source.title} | {file_path}]\n{block}"
        chunks.append(
            DocumentChunk(
                chunk_id=_make_chunk_id(source.source_id, file_path, len(chunks), situated),
                text=situated,
                metadata=_build_metadata(source, file_path),
            )
        )
    return chunks


def chunk_document(text: str, source: SourceRecord, file_path: str) -> list[DocumentChunk]:
    """Dispatch to the appropriate structure-aware chunker for the file and source type."""
    if source.source_type == "rulebook":
        return chunk_rulebook(text, source, file_path)
    if file_path.endswith(".py"):
        return chunk_python_ast(text, source, file_path)
    if file_path.endswith((".md", ".markdown")):
        return chunk_markdown(text, source, file_path)
    return chunk_plain_text(text, source, file_path)
