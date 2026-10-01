"""outer.v15.M3b — app-v2 formats + tag + tree capture."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
TREE = APP / "snapshots" / "app-v2.TREE"
TAGS = APP / "snapshots" / "TAGS"
V2 = APP / "docs" / "specs" / "SPEC.v2-todo-list-cli-output-formats.md"


class AppV2(unittest.TestCase):
    def test_v2_implemented_and_tree(self):
        self.assertTrue(V2.is_file())
        self.assertNotIn("(Status: PENDING)", V2.read_text(encoding="utf-8"))
        self.assertTrue(TREE.is_file())
        self.assertGreater(TREE.stat().st_size, 0)

    def test_tag_or_freeze(self):
        tags = subprocess.run(
            ["git", "tag", "-l", "app-v2"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        if tags == "app-v2":
            return
        self.assertTrue(TAGS.is_file())
        self.assertIn("app-v2", TAGS.read_text(encoding="utf-8"))

    def test_format_tests_exist(self):
        suite = (APP / "src/test/scala/todo/render/RendererSuite.scala").read_text(encoding="utf-8")
        self.assertIn("renderJson", suite)
        self.assertIn("markdown", suite.lower())


if __name__ == "__main__":
    unittest.main()
