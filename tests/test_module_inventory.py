import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.memory.inventory import (  # noqa: E402
    classify_doc_file,
    evaluate_inventory,
    modules_without_documents,
    render_gap_report_markdown,
)


class TestModuleInventory(unittest.TestCase):
    def test_classify_doc_file_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = classify_doc_file(root / "missing.md")
            self.assertEqual(missing.status, "missing")

            stub = root / "stub.md"
            stub.write_text("# TODO\n", encoding="utf-8")
            self.assertEqual(classify_doc_file(stub).status, "stub_only")

            full = root / "full.md"
            full.write_text("# Module\n" + ("Detail line.\n" * 10), encoding="utf-8")
            self.assertEqual(classify_doc_file(full).status, "documented")

    def test_evaluate_repo_inventory_and_render_markdown(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config_path = repo_root / "configs" / "module_inventory.json"
        report = evaluate_inventory(config_path, base_dir=repo_root)

        self.assertGreaterEqual(report.total_modules, 24)
        gaps = modules_without_documents(report)
        gap_ids = {entry.spec.module_id for entry in gaps}
        self.assertIn("docs_architecture", gap_ids)
        self.assertIn("rag_chatbot", gap_ids)

        md = render_gap_report_markdown(report)
        self.assertIn("## Modules With No Substantive Documentation", md)
        self.assertIn("`docs/architecture.md`", md)

    def test_evaluate_inventory_in_temp_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok.md").write_text("x" * 100, encoding="utf-8")
            cfg = root / "inv.json"
            cfg.write_text(
                json.dumps(
                    {
                        "modules": [
                            {
                                "module_id": "m1",
                                "name": "M1",
                                "category": "subteam",
                                "lead_or_owner": "Team",
                                "priority_phase": "P1",
                                "expected_docs": ["ok.md"],
                            },
                            {
                                "module_id": "m2",
                                "name": "M2",
                                "category": "agentic_package",
                                "lead_or_owner": "Team",
                                "priority_phase": "P2",
                                "expected_docs": ["nope.md"],
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            report = evaluate_inventory(cfg, base_dir=root)
            self.assertEqual(report.documented_count, 1)
            self.assertEqual(report.missing_count, 1)


if __name__ == "__main__":
    unittest.main()
