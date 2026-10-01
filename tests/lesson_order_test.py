import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = ROOT / "scripts" / "lesson-order"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
sys.path.insert(0, str(ROOT / "scripts"))
import journey  # noqa: E402


FIXTURE = """Intro text stays out of the order.

# Notes

Not a lesson slug heading.

# refine-1: First

body of refine-1
more lines

# refine-1a: Second

body of refine-1a

# Stack

Still not a lesson.

# skills-2: Last

tail
"""


class LessonOrder(unittest.TestCase):
    def test_awk_and_python_print_the_same_fixture_order(self):
        path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "JOURNEY.md"
        path.write_text(FIXTURE)
        awk = subprocess.run([str(ORDER), str(path)], capture_output=True, text=True, check=True)
        self.assertEqual(awk.stdout, "refine-1\nrefine-1a\nskills-2\n")
        self.assertEqual(journey.order_path(path), ["refine-1", "refine-1a", "skills-2"])

    def test_section_stops_at_the_next_lesson_heading(self):
        text = FIXTURE
        first = journey.section(text, "refine-1")
        self.assertTrue(first.startswith("# refine-1: First\n"))
        self.assertIn("body of refine-1", first)
        self.assertNotIn("# refine-1a:", first)
        second = journey.section(text, "refine-1a")
        self.assertTrue(second.startswith("# refine-1a: Second\n"))
        self.assertNotIn("# skills-2:", second)

    def test_live_journey_has_no_phase_headings_and_matches_lesson_order(self):
        text = JOURNEY.read_text()
        self.assertNotIn("\n# Refine\n", "\n" + text)
        self.assertNotIn("\n# Implement\n", "\n" + text)
        self.assertFalse(any(line.startswith("# Refine") for line in text.splitlines()))
        self.assertFalse(any(line.startswith("# Implement") for line in text.splitlines()))
        awk = subprocess.run([str(ORDER), str(JOURNEY)], capture_output=True, text=True, check=True)
        ids = awk.stdout.splitlines()
        self.assertEqual(ids, journey.order_path(JOURNEY))
        self.assertEqual(
            ids,
            [
                "refine-1",
                "refine-1a",
                "refine-2",
                "refine-3",
                "refine-4",
                "refine-5",
                "refine-6",
                "implement-1",
                "implement-1b",
                "implement-2",
                "quality-gates-1",
                "refine-7",
                "quality-gates-2",
                "skills-1",
                "skills-2",
                "quality-gates-3",
                "quality-gates-4",
            ],
        )
        shown = subprocess.run(["just", "--show", "prepare"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("scripts/lesson-order", shown.stdout)
        self.assertNotIn('ORDER=(', shown.stdout)


if __name__ == "__main__":
    unittest.main()
