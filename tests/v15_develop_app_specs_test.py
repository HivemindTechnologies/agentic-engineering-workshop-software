"""outer.v15.M2a–M2c — develop_app.v2–v4 product SPECs under app/docs/specs."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_SPECS = ROOT / "app" / "docs" / "specs"
CHECK = ROOT / "scripts" / "spec-check"
V1 = APP_SPECS / "SPEC.v1-todo-list-cli-mvp.md"
V2 = APP_SPECS / "SPEC.v2-todo-list-cli-output-formats.md"
V3 = APP_SPECS / "SPEC.v3-todo-list-cli-config.md"
V4 = APP_SPECS / "SPEC.v4-todo-list-cli-planning.md"


def check(path: Path):
    return subprocess.run([str(CHECK), str(path)], capture_output=True, text=True)


class DevelopAppSpecs(unittest.TestCase):
    def test_v1_baseline_from_quality_gates_3_exists(self):
        self.assertTrue(V1.is_file())
        self.assertEqual(check(V1).returncode, 0, check(V1).stderr)

    def test_v2_covers_json_markdown_ansi(self):
        self.assertTrue(V2.is_file())
        text = V2.read_text(encoding="utf-8")
        for needle in ("JSON", "Markdown", "ANSI", "develop_app.v2"):
            self.assertIn(needle, text)
        self.assertEqual(check(V2).returncode, 0, check(V2).stderr)

    def test_v3_pins_pureconfig_and_env(self):
        self.assertTrue(V3.is_file())
        text = V3.read_text(encoding="utf-8")
        for needle in ("PureConfig", "0.17.8", "TODO_STORE", "application.conf", "develop_app.v3"):
            self.assertIn(needle, text)
        self.assertEqual(check(V3).returncode, 0, check(V3).stderr)

    def test_v4_covers_planning_and_assignees(self):
        self.assertTrue(V4.is_file())
        text = V4.read_text(encoding="utf-8")
        for needle in ("due date", "priority", "tags", "assignee", "email", "develop_app.v4"):
            self.assertIn(needle, text)
        self.assertEqual(check(V4).returncode, 0, check(V4).stderr)


if __name__ == "__main__":
    unittest.main()
