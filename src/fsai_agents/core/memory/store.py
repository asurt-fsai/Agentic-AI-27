from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from fsai_agents.core.memory.models import DocumentChunk

PGVECTOR_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    sensitivity TEXT NOT NULL CHECK (sensitivity IN ('api-ok', 'local-only')),
    acl TEXT NOT NULL CHECK (acl IN ('public', 'team-internal', 'maintainer-only')),
    namespace TEXT NOT NULL,
    file_path TEXT NOT NULL,
    title TEXT NOT NULL,
    edition TEXT NOT NULL DEFAULT '',
    heading_path TEXT NOT NULL DEFAULT '',
    symbol TEXT NOT NULL DEFAULT '',
    clause_id TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    embedding vector(1024),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_sensitivity
    ON knowledge_chunks (sensitivity, acl, namespace);
""".strip()


class ChunkStore(Protocol):
    """Persistence interface shared by JsonlChunkStore and future pgvector stores."""

    def upsert(self, chunks: list[DocumentChunk]) -> int: ...

    def list_chunks(
        self,
        *,
        sensitivity: str | None = None,
        source_id: str | None = None,
    ) -> list[DocumentChunk]: ...


class JsonlChunkStore:
    """Deterministic local JSONL store for P1 offline indexing and CI tests."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _load_all(self) -> dict[str, DocumentChunk]:
        if not self.path.exists():
            return {}
        records: dict[str, DocumentChunk] = {}
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    chunk = DocumentChunk.from_dict(json.loads(line))
                    records[chunk.chunk_id] = chunk
        return records

    def upsert(self, chunks: list[DocumentChunk]) -> int:
        existing = self._load_all()
        for chunk in chunks:
            existing[chunk.chunk_id] = chunk
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            for chunk in existing.values():
                handle.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
        return len(chunks)

    def list_chunks(
        self,
        *,
        sensitivity: str | None = None,
        source_id: str | None = None,
    ) -> list[DocumentChunk]:
        chunks = list(self._load_all().values())
        if sensitivity is not None:
            chunks = [c for c in chunks if c.metadata.sensitivity == sensitivity]
        if source_id is not None:
            chunks = [c for c in chunks if c.metadata.source_id == source_id]
        return chunks
