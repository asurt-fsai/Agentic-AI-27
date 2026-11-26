from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from fsai_agents.core.policy.sensitivity import AccessLevel, SensitivityTag

SourceType = Literal["rulebook", "repo", "notion"]
ParserChoice = Literal["local", "docling", "llamaparse"]


@dataclass(frozen=True)
class SourceRecord:
    """Manifest entry describing one knowledge source and its policy tags."""

    source_id: str
    title: str
    source_type: SourceType
    path: str
    sensitivity: SensitivityTag
    acl: AccessLevel = AccessLevel.TEAM_INTERNAL
    namespace: str = "ns_rules_ops"
    edition: str = ""
    parser: ParserChoice = "local"
    include_globs: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SourceRecord:
        return cls(
            source_id=str(raw["source_id"]),
            title=str(raw["title"]),
            source_type=raw["source_type"],
            path=str(raw["path"]),
            sensitivity=SensitivityTag(raw["sensitivity"]),
            acl=AccessLevel(raw.get("acl", AccessLevel.TEAM_INTERNAL.value)),
            namespace=str(raw.get("namespace", "ns_rules_ops")),
            edition=str(raw.get("edition", "")),
            parser=raw.get("parser", "local"),
            include_globs=tuple(raw.get("include_globs", ())),
        )


@dataclass(frozen=True)
class ChunkMetadata:
    """Metadata stored alongside every indexed chunk for filtering and citations."""

    source_id: str
    source_type: SourceType
    sensitivity: str
    acl: str
    namespace: str
    file_path: str
    title: str
    edition: str = ""
    heading_path: str = ""
    symbol: str = ""
    clause_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DocumentChunk:
    """Single unit of retrieved knowledge with situating context and policy tags."""

    chunk_id: str
    text: str
    metadata: ChunkMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> DocumentChunk:
        meta = dict(raw["metadata"])
        return cls(
            chunk_id=str(raw["chunk_id"]),
            text=str(raw["text"]),
            metadata=ChunkMetadata(**meta),
        )


@dataclass
class IngestionSummary:
    """Summary returned after ingesting a source or manifest."""

    indexed_sources: list[str] = field(default_factory=list)
    skipped_excluded: list[tuple[str, str]] = field(default_factory=list)
    skipped_missing: list[str] = field(default_factory=list)
    total_chunks: int = 0
