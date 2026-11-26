import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.memory import JsonlChunkStore, ingest_manifest, select_parser  # noqa: E402
from fsai_agents.core.memory.models import SourceRecord  # noqa: E402
from fsai_agents.core.policy import SensitivityTag  # noqa: E402


class TestIngestionPipeline(unittest.TestCase):
    def test_ingest_manifest_enforces_exclusions_and_tags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rules.md").write_text(
                "IN2.2.2 Static Inspection\nRamp to 200 rpm.\n",
                encoding="utf-8",
            )
            (root / "survey_sheet.csv").write_text("user,pain\nfoo,5\n", encoding="utf-8")
            (root / "secret_notes.md").write_text(
                "token=sk-ant-1234567890abcdef1234\n",
                encoding="utf-8",
            )
            (root / "notes.md").write_text("# Setup\nRun locally.\n", encoding="utf-8")

            manifest = {
                "sources": [
                    {
                        "source_id": "rules-2026",
                        "title": "FS-AI 2026 Rules",
                        "source_type": "rulebook",
                        "path": "rules.md",
                        "sensitivity": "api-ok",
                        "acl": "public",
                        "edition": "FS2026-v1",
                    },
                    {
                        "source_id": "team-notes",
                        "title": "Team Notes",
                        "source_type": "notion",
                        "path": "notes.md",
                        "sensitivity": "local-only",
                        "acl": "team-internal",
                    },
                    {
                        "source_id": "survey",
                        "title": "Survey",
                        "source_type": "notion",
                        "path": "survey_sheet.csv",
                        "sensitivity": "excluded",
                    },
                    {
                        "source_id": "leaked-notes",
                        "title": "Leaked",
                        "source_type": "notion",
                        "path": "secret_notes.md",
                        "sensitivity": "local-only",
                    },
                ]
            }
            manifest_path = root / "sources.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            store = JsonlChunkStore(root / "index.jsonl")
            summary = ingest_manifest(manifest_path, store, base_dir=root)

            self.assertIn("rules-2026", summary.indexed_sources)
            self.assertIn("team-notes", summary.indexed_sources)
            self.assertEqual([s for s, _ in summary.skipped_excluded], ["survey", "leaked-notes"])

            all_chunks = store.list_chunks()
            self.assertEqual(len(all_chunks), 2)
            self.assertEqual(len(store.list_chunks(sensitivity="api-ok")), 1)
            self.assertEqual(len(store.list_chunks(sensitivity="local-only")), 1)

            # Idempotent re-run does not duplicate chunks
            ingest_manifest(manifest_path, store, base_dir=root)
            self.assertEqual(len(store.list_chunks()), 2)

    def test_select_parser_blocks_llamaparse_on_local_only_pdf(self) -> None:
        source = SourceRecord(
            source_id="private-pdf",
            title="Private",
            source_type="notion",
            path="private.pdf",
            sensitivity=SensitivityTag.LOCAL_ONLY,
            parser="llamaparse",
        )
        with self.assertRaises(PermissionError):
            select_parser(Path("private.pdf"), source)


if __name__ == "__main__":
    unittest.main()
