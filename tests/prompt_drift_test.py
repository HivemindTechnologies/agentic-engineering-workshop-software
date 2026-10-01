import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prompt-distance"
JUSTFILE = ROOT / "justfile"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
BASELINE = ROOT / "workshop" / "prompt-distance-baseline.txt"

BOARD = """# refine-1: One

*PROMPT TO TEST*
```
alpha
```

# refine-1a: Two

*PROMPT TO TEST*
```
beta
```

# refine-2: Three

*PROMPT TO TEST*
```
gamma
```
"""

# refine-1: previous=absent next=+1.0000; refine-1a: previous=+1.0000 next=+0.0000;
# refine-2: previous=+0.0000 next=absent — same fixture geometry as prompt_distance_test.py.
VECTORS = {"refine-1": [1, 0], "refine-1a": [1, 0], "refine-2": [0, 1]}


class PromptDriftCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.journey = self.tmp / "JOURNEY.md"
        self.journey.write_text(BOARD)
        self.vectors_path = self.tmp / "vectors.json"
        self.vectors_path.write_text(json.dumps(VECTORS))
        self.baseline = self.tmp / "baseline.txt"

    def run_check(self, threshold=None):
        args = [
            str(SCRIPT),
            str(self.journey),
            "--vectors",
            str(self.vectors_path),
            "--check-baseline",
            str(self.baseline),
        ]
        if threshold is not None:
            args.extend(["--threshold", str(threshold)])
        return subprocess.run(args, capture_output=True, text=True)

    def test_an_identical_board_passes(self):
        self.baseline.write_text(
            "\n".join(
                [
                    "refine-1     previous= absent next=+1.0000",
                    "refine-1a    previous=+1.0000 next=+0.0000",
                    "refine-2     previous=+0.0000 next= absent",
                ]
            )
            + "\n"
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_drift_within_threshold_passes(self):
        self.baseline.write_text("refine-1a    previous=+0.9600 next=+0.0000\n")
        result = self.run_check(threshold=0.05)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_drift_past_threshold_fails_and_names_lesson_and_field(self):
        self.baseline.write_text("refine-1a    previous=+0.5000 next=+0.0000\n")
        result = self.run_check(threshold=0.05)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refine-1a previous baseline=+0.5000 current=+1.0000", result.stdout)
        self.assertNotIn("refine-1a next baseline", result.stdout)

    def test_absent_versus_a_number_fails_unconditionally(self):
        self.baseline.write_text("refine-1     previous=+0.1000 next=+1.0000\n")
        result = self.run_check(threshold=1.0)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refine-1 previous baseline=+0.1000 current=absent", result.stdout)

    def test_absent_both_sides_passes(self):
        self.baseline.write_text("refine-1     previous= absent next=+1.0000\n")
        result = self.run_check(threshold=0.0)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_lesson_missing_from_the_current_journey_fails_and_names_it(self):
        self.baseline.write_text("refine-3     previous=+0.5000 next= absent\n")
        result = self.run_check(threshold=1.0)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refine-3", result.stdout)

    def test_a_new_lesson_absent_from_the_baseline_does_not_fail(self):
        self.baseline.write_text("refine-1a    previous=+1.0000 next=+0.0000\n")
        result = self.run_check(threshold=0.0)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_without_check_baseline_behavior_is_unchanged(self):
        result = subprocess.run(
            [str(SCRIPT), str(self.journey), "--vectors", str(self.vectors_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("segment", result.stdout)

    def test_a_missing_baseline_file_is_a_script_error(self):
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(self.baseline), result.stderr)

    def test_freeze_recipe_writes_only_lesson_lines(self):
        text = JUSTFILE.read_text()
        self.assertIn("prompt-distance-freeze:", text)
        self.assertIn("prompt-distance-baseline.txt", text)

    def test_drift_check_recipe_uses_the_committed_baseline(self):
        text = JUSTFILE.read_text()
        self.assertIn("prompt-drift-check:", text)
        recipe = text.split("prompt-drift-check:", 1)[1].split("\n\n", 1)[0]
        self.assertIn("--check-baseline", recipe)
        self.assertIn("workshop/prompt-distance-baseline.txt", recipe)

    def test_the_real_baseline_currently_passes_the_real_journey(self):
        if not BASELINE.is_file():
            self.skipTest("no baseline frozen yet")
        result = subprocess.run(
            [str(SCRIPT), str(JOURNEY), "--check-baseline", str(BASELINE)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
