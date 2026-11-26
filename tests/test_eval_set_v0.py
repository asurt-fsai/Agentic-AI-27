import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.run_evals import run  # noqa: E402


class TestEvalSetV0(unittest.TestCase):
    def test_v0_suite_structure_and_counts(self) -> None:
        cases_path = Path(__file__).resolve().parents[1] / "evals" / "cases" / "v0.jsonl"
        cases = [
            json.loads(line)
            for line in cases_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(cases), 30)
        self.assertEqual([c["id"] for c in cases], [f"E{i}" for i in range(1, 31)])

        categories: dict[str, int] = {}
        for case in cases:
            for key in ("id", "category", "question", "reference_answer", "source_id"):
                self.assertIn(key, case)
                self.assertTrue(str(case[key]).strip())
            categories[case["category"]] = categories.get(case["category"], 0) + 1

        self.assertEqual(categories, {"rulebook": 10, "stack": 10, "handover": 10})
        traps = [c["id"] for c in cases if c.get("trap")]
        self.assertEqual(traps, [f"E{i}" for i in range(23, 31)])

    def test_reference_answers_score_30_of_30(self) -> None:
        root = Path(__file__).resolve().parents[1]
        passed, total = run(
            str(root / "evals" / "cases" / "v0.jsonl"),
            str(root / "evals" / "answers_reference_v0.jsonl"),
        )
        self.assertEqual(total, 30)
        self.assertEqual(passed, 30)


if __name__ == "__main__":
    unittest.main()
