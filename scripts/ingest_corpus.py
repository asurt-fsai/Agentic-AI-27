"""Run T19/T20 corpus ingestion from a source manifest into a local JSONL index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.memory import JsonlChunkStore, ingest_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest sources defined in a T19 manifest.")
    parser.add_argument("--manifest", default="configs/sources.json", help="Path to sources JSON.")
    parser.add_argument("--base-dir", default=".", help="Base directory for relative paths.")
    parser.add_argument("--out", default="data/index.jsonl", help="Output JSONL chunk store path.")
    args = parser.parse_args()

    store = JsonlChunkStore(Path(args.out))
    summary = ingest_manifest(Path(args.manifest), store, base_dir=Path(args.base_dir))
    print(f"Indexed sources ({len(summary.indexed_sources)}): {summary.indexed_sources}")
    print(f"Skipped excluded ({len(summary.skipped_excluded)}): {summary.skipped_excluded}")
    print(f"Skipped missing ({len(summary.skipped_missing)}): {summary.skipped_missing}")
    print(f"Total chunks upserted: {summary.total_chunks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
