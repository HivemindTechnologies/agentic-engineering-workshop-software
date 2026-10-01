import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBID = ROOT / "scripts" / "session-bash-forbid"
FORBIDS = ROOT / "workshop" / "session-bash-forbids.txt"
WOW = ROOT / "workshop" / "material" / "refine-4" / "docs" / "rules" / "WOW.md"
BASE_CLAUDE = ROOT / "workshop" / "material" / "00-base" / "CLAUDE.md"
REFINE6 = ROOT / "workshop" / "material" / "refine-6" / "docs" / "specs" / "SPEC.v1-todo-list-cli-mvp.md"


def session_with_bash(command: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    path = tmp / "session.jsonl"
    event = {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "name": "Bash",
                    "input": {"command": command},
                }
            ],
        },
    }
    path.write_text(json.dumps(event) + "\n")
    return path


class SessionBashForbid(unittest.TestCase):
    def test_maven_metadata_curl_is_forbidden(self):
        session = session_with_bash(
            'curl -s https://repo1.maven.org/maven2/org/scala-lang/scala3-library_3/maven-metadata.xml'
        )
        result = subprocess.run(
            ["python3", str(FORBID), str(FORBIDS), str(session)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("maven-metadata.xml", result.stderr)

    def test_broad_find_is_forbidden(self):
        session = session_with_bash("find . -not -path './.git/*' -type f | sort")
        result = subprocess.run(
            ["python3", str(FORBID), str(FORBIDS), str(session)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("find . -not -path", result.stderr)

    def test_clean_write_session_passes(self):
        session = session_with_bash("mkdir -p docs/specs")
        result = subprocess.run(
            ["python3", str(FORBID), str(FORBIDS), str(session)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dress_rehearsal_implement_1_still_trips_the_gate(self):
        session = (
            ROOT
            / "workshop"
            / "results"
            / "implement-1"
            / "2026-09-29-02-38-26"
            / "session.jsonl"
        )
        if not session.is_file():
            self.skipTest("dress-rehearsal session not present")
        result = subprocess.run(
            ["python3", str(FORBID), str(FORBIDS), str(session)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            "maven-metadata.xml" in result.stderr or "find . -not -path" in result.stderr,
            result.stderr,
        )


class InteractionMaterial(unittest.TestCase):
    def test_wow_pins_dependency_versions(self):
        text = WOW.read_text()
        for needle in ("3.3.4", "2.12.0", "3.5.7", "0.3.0", "1.0.3", "Do not `curl`"):
            self.assertIn(needle, text)

    def test_refine6_spec_pins_versions_for_implement_1(self):
        text = REFINE6.read_text()
        self.assertIn("3.3.4", text)
        self.assertIn("2.12.0", text)
        self.assertIn("do not look up versions on Maven", text)

    def test_base_claude_md_discourages_broad_find(self):
        text = BASE_CLAUDE.read_text()
        self.assertIn("Do not rediscover the tree", text)
        self.assertIn("docs/specs/", text)


if __name__ == "__main__":
    unittest.main()
