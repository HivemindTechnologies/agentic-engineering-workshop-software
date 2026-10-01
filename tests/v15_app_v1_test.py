"""outer.v15.M3a — app/ holds develop_*.v1; tag app-v1; check green."""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
TAGS_FILE = APP / "snapshots" / "TAGS"
TREE = APP / "snapshots" / "app-v1.TREE"
V1 = APP / "docs" / "specs" / "SPEC.v1-todo-list-cli-mvp.md"


class AppV1(unittest.TestCase):
    def test_app_layout_and_v1_complete(self):
        self.assertTrue((APP / "build.sbt").is_file())
        self.assertTrue((APP / "src" / "main" / "scala" / "todo" / "Cli.scala").is_file())
        self.assertTrue(V1.is_file())
        text = V1.read_text(encoding="utf-8")
        self.assertNotIn("(Status: PENDING)", text)
        self.assertTrue(TREE.is_file())
        self.assertGreater(TREE.stat().st_size, 0)

    def test_app_v1_tag_or_freeze(self):
        # Prefer live git tag; fall back to committed freeze file listing tag SHA.
        tags = subprocess.run(
            ["git", "tag", "-l", "app-v1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if tags == "app-v1":
            return
        self.assertTrue(TAGS_FILE.is_file(), "missing git tag app-v1 and snapshots/TAGS freeze")
        freeze = TAGS_FILE.read_text(encoding="utf-8")
        self.assertIn("app-v1", freeze)

    def test_just_check_exits_0(self):
        env = os.environ.copy()
        # Avoid interactive sbt prompts in CI-like runs.
        result = subprocess.run(
            ["just", "check"],
            cwd=APP,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
