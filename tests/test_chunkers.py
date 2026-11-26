import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.memory import (  # noqa: E402
    SourceRecord,
    chunk_document,
    chunk_markdown,
    chunk_python_ast,
    chunk_rulebook,
)
from fsai_agents.core.policy import AccessLevel, SensitivityTag  # noqa: E402


class TestChunkers(unittest.TestCase):
    def test_markdown_chunker_preserves_tables_and_code_blocks(self) -> None:
        source = SourceRecord(
            source_id="notion-doc",
            title="Onboarding",
            source_type="notion",
            path="docs/onboarding.md",
            sensitivity=SensitivityTag.LOCAL_ONLY,
            acl=AccessLevel.TEAM_INTERNAL,
        )
        md = (
            "# Overview\n"
            "Intro paragraph.\n\n"
            "## Table Section\n"
            "| Col A | Col B |\n"
            "| --- | --- |\n"
            "| 1 | 2 |\n\n"
            "## Code Section\n"
            "```python\n"
            "# not a markdown heading\n"
            "def hello():\n"
            "    return 'world'\n"
            "```\n"
        )
        chunks = chunk_markdown(md, source, "docs/onboarding.md")
        self.assertEqual(len(chunks), 3)
        self.assertIn("| Col A | Col B |\n| --- | --- |\n| 1 | 2 |", chunks[1].text)
        self.assertEqual(chunks[2].metadata.heading_path, "Overview > Code Section")
        self.assertIn("# not a markdown heading", chunks[2].text)

    def test_rulebook_chunker_extracts_clause_ids_and_edition(self) -> None:
        source = SourceRecord(
            source_id="fs-ai-2026",
            title="FS-AI 2026 Rules",
            source_type="rulebook",
            path="rules.md",
            sensitivity=SensitivityTag.API_OK,
            acl=AccessLevel.PUBLIC,
            edition="FS2026-v1",
        )
        text = (
            "IN2.2.2 Static Inspection A\n"
            "Ramp drivetrain to 200 rpm in 10 s.\n\n"
            "D1.3.1 Start Area Telemetry\n"
            "Monitoring devices may not transmit commands.\n"
        )
        chunks = chunk_rulebook(text, source, "rules.md")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].metadata.clause_id, "IN2.2.2")
        self.assertEqual(chunks[0].metadata.edition, "FS2026-v1")
        self.assertEqual(chunks[1].metadata.clause_id, "D1.3.1")

    def test_python_ast_chunker_splits_functions_and_classes(self) -> None:
        source = SourceRecord(
            source_id="repo",
            title="Repo",
            source_type="repo",
            path="src/mod.py",
            sensitivity=SensitivityTag.API_OK,
        )
        code = (
            "CONSTANT = 42\n\n"
            "def helper(x: int) -> int:\n"
            "    return x + 1\n\n"
            "class Runner:\n"
            "    def run(self) -> None:\n"
            "        pass\n"
        )
        chunks = chunk_python_ast(code, source, "src/mod.py")
        symbols = [c.metadata.symbol for c in chunks]
        self.assertEqual(symbols, ["<module>", "helper", "Runner"])
        self.assertEqual(chunk_document(code, source, "src/mod.py")[1].metadata.symbol, "helper")


if __name__ == "__main__":
    unittest.main()
