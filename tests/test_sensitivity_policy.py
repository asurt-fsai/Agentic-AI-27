import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.policy import (  # noqa: E402
    SensitivityTag,
    can_index,
    can_send_to_cloud_parser,
    enforce_cloud_parser_policy,
    find_sensitive_content,
    is_path_excluded,
)


class TestSensitivityPolicy(unittest.TestCase):
    def test_excluded_paths_are_blocked(self) -> None:
        for path in [
            ".env",
            "config/.env.local",
            "data/subteam_survey_2026.csv",
            "docs/alumni_contacts_slide_51.md",
            "secrets/github_token.txt",
        ]:
            excluded, reason = is_path_excluded(path)
            self.assertTrue(excluded, f"Expected {path} to be excluded")
            self.assertIsNotNone(reason)

    def test_normal_paths_are_allowed(self) -> None:
        for path in ["README.md", "docs/hardware.md", "src/fsai_agents/core/llm/models.py"]:
            excluded, _ = is_path_excluded(path)
            self.assertFalse(excluded, f"Unexpected exclusion for {path}")

    def test_cloud_parser_is_restricted_to_api_ok(self) -> None:
        self.assertTrue(can_send_to_cloud_parser(SensitivityTag.API_OK))
        self.assertFalse(can_send_to_cloud_parser(SensitivityTag.LOCAL_ONLY))
        self.assertFalse(can_send_to_cloud_parser(SensitivityTag.EXCLUDED))

        enforce_cloud_parser_policy(SensitivityTag.API_OK, "rules")
        with self.assertRaises(PermissionError):
            enforce_cloud_parser_policy(SensitivityTag.LOCAL_ONLY, "ros2-repo")
        with self.assertRaises(PermissionError):
            enforce_cloud_parser_policy(SensitivityTag.EXCLUDED, "survey")

    def test_can_index_blocks_excluded(self) -> None:
        self.assertTrue(can_index(SensitivityTag.API_OK))
        self.assertTrue(can_index(SensitivityTag.LOCAL_ONLY))
        self.assertFalse(can_index(SensitivityTag.EXCLUDED))

    def test_find_sensitive_content_detects_keys(self) -> None:
        self.assertEqual(find_sensitive_content("normal documentation text"), [])
        self.assertIn(
            "anthropic_key",
            find_sensitive_content("ANTHROPIC_API_KEY=sk-ant-1234567890abcdef1234"),
        )


if __name__ == "__main__":
    unittest.main()
