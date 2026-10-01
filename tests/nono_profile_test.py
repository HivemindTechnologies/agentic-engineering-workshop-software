import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NONO = ROOT / "nono.json"
STRICT = ROOT / "nono-strict.json"
ENSURE = ROOT / "scripts" / "nono-ensure-claude-dirs.sh"
REMOTE = "nolabs-ai/claude"


class NonoProfileInline(unittest.TestCase):
    def _extends_values(self, data):
        extends = data.get("extends")
        if extends is None:
            return []
        if isinstance(extends, list):
            return list(extends)
        return [extends]

    def test_nono_json_does_not_extend_the_remote_claude_pack(self):
        data = json.loads(NONO.read_text())
        self.assertNotIn(REMOTE, self._extends_values(data))
        self.assertEqual(data["extends"], "default")

    def test_nono_json_carries_inlined_claude_grants(self):
        data = json.loads(NONO.read_text())
        groups = data["groups"]["include"]
        names = {g if isinstance(g, str) else g["name"] for g in groups}
        for needed in (
            "deny_credentials",
            "java_runtime",
            "node_runtime",
            "unlink_protection",
            "git_config",
        ):
            self.assertIn(needed, names)
        allow = data["filesystem"]["allow"]
        allow_paths = {a if isinstance(a, str) else a["path"] for a in allow}
        self.assertIn("$WORKDIR", allow_paths)
        self.assertIn("$HOME/.claude", allow_paths)
        self.assertTrue(ENSURE.is_file(), ENSURE)
        self.assertIn("nono-ensure-claude-dirs.sh", data["session_hooks"]["before"]["script"])

    def test_nono_strict_does_not_extend_the_remote_claude_pack(self):
        data = json.loads(STRICT.read_text())
        self.assertNotIn(REMOTE, self._extends_values(data))
        self.assertEqual(data["extends"], "default")

    def test_nono_validates_the_inlined_profile_without_the_pack(self):
        nono = shutil.which("nono")
        if nono is None:
            self.skipTest("nono not on PATH")
        result = subprocess.run(
            [nono, "profile", "validate", str(NONO)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("valid", (result.stdout + result.stderr).lower())
        strict = subprocess.run(
            [nono, "profile", "validate", str(STRICT)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(strict.returncode, 0, strict.stdout + strict.stderr)


if __name__ == "__main__":
    unittest.main()
