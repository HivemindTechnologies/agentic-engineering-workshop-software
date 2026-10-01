"""outer.v17.M3 — deck smoothness skill + mechanical presentation-check."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "presentation-check"
SKILL = ROOT / ".claude" / "skills" / "deck-smoothness" / "SKILL.md"
JUST = ROOT / "justfile"


class DeckSmoothnessM3(unittest.TestCase):
    def test_skill_and_recipe_exist(self):
        self.assertTrue(SKILL.is_file())
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("assembled", text.lower())
        self.assertIn("Steckbrief", text)
        self.assertIn("showcase", text.lower())
        self.assertIn("findings", text.lower())
        just = JUST.read_text(encoding="utf-8")
        self.assertRegex(just, r"(?m)^present-check-smooth\b")
        shown = subprocess.run(
            ["just", "--show", "present-check-smooth"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("presentation-check", shown.stdout)

    def test_live_presentation_check_passes(self):
        result = subprocess.run(
            ["python3", str(CHECK)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_fixture_missing_lesson_file_fails_mechanical_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            presentation = root / "presentation"
            lessons = presentation / "lessons"
            lessons.mkdir(parents=True)
            (presentation / "bridge").mkdir()
            (presentation / "bridge" / "bindings.yaml").write_text("[]\n", encoding="utf-8")
            (presentation / "deck-software-part1.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    title: Fixture
                    ---
                    <h1 class="title">Fixture</h1>
                    <!-- lessons:
                    == Part 1
                    -- Demo
                    missing99
                    -->
                    """
                ),
                encoding="utf-8",
            )
            (presentation / "deck-software-part2.md").write_text(
                "# empty\n<!-- lessons:\n== Part 2\n-- X\n-->\n",
                encoding="utf-8",
            )
            journey = root / "JOURNEY.md"
            journey.write_text("# none: x\n\nprose\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(CHECK),
                    "--presentation",
                    str(presentation),
                    "--journey",
                    str(journey),
                    "--bindings",
                    str(presentation / "bridge" / "bindings.yaml"),
                    "--results",
                    str(root / "results"),
                    "--skip-bridge",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing99", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
