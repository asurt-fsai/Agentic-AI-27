from __future__ import annotations

import json
from pathlib import Path

from fsai_agents.core.memory.chunkers import chunk_document
from fsai_agents.core.memory.models import IngestionSummary, SourceRecord
from fsai_agents.core.memory.parsers import DocumentParser, select_parser
from fsai_agents.core.memory.store import ChunkStore
from fsai_agents.core.policy.sensitivity import (
    can_index,
    find_sensitive_content,
    is_path_excluded,
)


def load_manifest(manifest_path: Path) -> list[SourceRecord]:
    """Load T19 source records from a JSON manifest."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [SourceRecord.from_dict(entry) for entry in data.get("sources", [])]


def _collect_files(source: SourceRecord, base_dir: Path) -> list[Path]:
    target = (base_dir / source.path).resolve()
    if not target.exists():
        return []
    if target.is_file():
        return [target]

    globs = source.include_globs or ("**/*.md", "**/*.py")
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in globs:
        for candidate in sorted(target.glob(pattern)):
            if candidate.is_file() and candidate not in seen:
                seen.add(candidate)
                files.append(candidate)
    return files


def ingest_source(
    source: SourceRecord,
    store: ChunkStore,
    *,
    base_dir: Path = Path("."),
    parser_override: DocumentParser | None = None,
) -> tuple[int, str | None]:
    """Ingest one source if permitted by sensitivity and path/content exclusion rules."""
    if not can_index(source.sensitivity):
        return 0, f"sensitivity={source.sensitivity.value}"

    excluded, reason = is_path_excluded(source.path)
    if excluded:
        return 0, reason

    files = _collect_files(source, base_dir)
    if not files:
        return -1, "path_missing"

    total_chunks = 0
    for file_path in files:
        rel_path = file_path.as_posix()
        try:
            rel_path = file_path.relative_to(base_dir.resolve()).as_posix()
        except ValueError:
            pass

        file_excluded, _ = is_path_excluded(rel_path)
        if file_excluded:
            continue

        parser = parser_override or select_parser(file_path, source)
        text = parser.parse(file_path, source)
        if find_sensitive_content(text):
            continue

        chunks = chunk_document(text, source, rel_path)
        if chunks:
            total_chunks += store.upsert(chunks)

    return total_chunks, None


def ingest_manifest(
    manifest_path: Path,
    store: ChunkStore,
    *,
    base_dir: Path = Path("."),
) -> IngestionSummary:
    """Ingest all permitted sources from a T19 manifest into the configured store."""
    summary = IngestionSummary()
    for source in load_manifest(manifest_path):
        count, reason = ingest_source(source, store, base_dir=base_dir)
        if count == -1:
            summary.skipped_missing.append(source.source_id)
        elif reason is not None:
            summary.skipped_excluded.append((source.source_id, reason))
        else:
            summary.indexed_sources.append(source.source_id)
            summary.total_chunks += count
    return summary
