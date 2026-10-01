import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "scripts" / "claude-home-seed"
SETTINGS = ROOT / "workshop" / "material" / "00-base" / ".claude" / "settings.json"
JUSTFILE = ROOT / "justfile"


class ClaudeHomeTrust(unittest.TestCase):
    def test_seed_marks_has_trust_dialog_accepted_for_the_project_root(self):
        tmp = Path(tempfile.mkdtemp())
        home = tmp / "claude-home"
        root = tmp / "develop"
        root.mkdir()
        result = subprocess.run(
            [str(SEED), str(home), str(root)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((home / ".claude.json").read_text())
        self.assertTrue(data["hasCompletedOnboarding"])
        self.assertTrue(data["projects"][str(root)]["hasTrustDialogAccepted"])

    def test_seed_preserves_existing_project_keys(self):
        tmp = Path(tempfile.mkdtemp())
        home = tmp / "claude-home"
        home.mkdir()
        root = str(tmp / "develop")
        (home / ".claude.json").write_text(
            json.dumps(
                {
                    "theme": "dark",
                    "projects": {root: {"allowedTools": ["Read"], "hasTrustDialogAccepted": False}},
                }
            )
        )
        result = subprocess.run(
            [str(SEED), str(home), root],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((home / ".claude.json").read_text())
        self.assertEqual(data["theme"], "dark")
        self.assertEqual(data["projects"][root]["allowedTools"], ["Read"])
        self.assertTrue(data["projects"][root]["hasTrustDialogAccepted"])

    def test_justfile_claude_home_uses_the_seed_script(self):
        text = JUSTFILE.read_text()
        self.assertIn("scripts/claude-home-seed", text)
        self.assertIn("{{sandbox}}/.claude-home {{sandbox}}", text)


class ClaudeAcceptEdits(unittest.TestCase):
    def test_base_settings_default_mode_is_accept_edits(self):
        data = json.loads(SETTINGS.read_text())
        self.assertEqual(data["permissions"]["defaultMode"], "acceptEdits")
        self.assertIn("hooks", data)

    def test_prepare_copies_accept_edits_into_develop(self):
        tmp = Path(tempfile.mkdtemp())
        work = tmp / "develop"
        record = tmp / "prepared-lesson"
        env = os.environ.copy()
        env["PREPARE_WORK"] = str(work)
        env["PREPARE_RECORD"] = str(record)
        env["GIT_AUTHOR_NAME"] = "Prepare"
        env["GIT_AUTHOR_EMAIL"] = "prepare@example.com"
        env["GIT_COMMITTER_NAME"] = "Prepare"
        env["GIT_COMMITTER_EMAIL"] = "prepare@example.com"
        result = subprocess.run(
            ["just", "prepare", "refine-1"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        settings = json.loads((work / ".claude" / "settings.json").read_text())
        self.assertEqual(settings["permissions"]["defaultMode"], "acceptEdits")


if __name__ == "__main__":
    unittest.main()
