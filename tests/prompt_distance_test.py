import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prompt-distance"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"

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


def run(journey, lesson="", vectors=None):
    args = [str(SCRIPT), str(journey)]
    if lesson:
        args.extend(["--lesson", lesson])
    if vectors is not None:
        path = journey.parent / "vectors.json"
        path.write_text(json.dumps(vectors))
        args.extend(["--vectors", str(path)])
    return subprocess.run(args, capture_output=True, text=True)


class PromptDistance(unittest.TestCase):
    def test_injected_vectors_print_one_and_zero_and_predecessors(self):
        journey = self.write(BOARD)
        before = journey.read_text()
        vectors = {
            "refine-1": [1, 0],
            "refine-1a": [1, 0],
            "refine-2": [0, 1],
        }
        result = run(journey, vectors=vectors)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "\n".join(
                [
                    "refine-1     previous= absent next=+1.0000",
                    "refine-1a    previous=+1.0000 next=+0.0000",
                    "refine-2     previous=+0.0000 next= absent",
                    "segment refine-1 refine-1a",
                    "segment refine-2 refine-2",
                    "",
                ]
            ),
        )
        self.assertNotIn("refine-1=", result.stdout)
        reference = (journey.parent / "prompt-distance.txt").read_text().splitlines()
        self.assertEqual(
            reference[1],
            "refine-1a    previous=+1.0000 next=+0.0000 refine-1=+1.0000",
        )
        self.assertEqual(journey.read_text(), before)

    def test_equal_neighbor_similarities_are_one_segment(self):
        journey = self.write(BOARD)
        vectors = {
            "refine-1": [1, 0],
            "refine-1a": [1, 0],
            "refine-2": [1, 0],
        }
        result = run(journey, vectors=vectors)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], "segment refine-1 refine-2")

    def test_one_lesson_prints_its_line_and_no_segments(self):
        journey = self.write(BOARD)
        vectors = {
            "refine-1": [1, 0],
            "refine-1a": [1, 0],
            "refine-2": [0, 1],
        }
        result = run(journey, lesson="refine-1a", vectors=vectors)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "refine-1a    previous=+1.0000 next=+0.0000\n")
        self.assertNotIn("segment", result.stdout)
        self.assertNotIn("refine-1=", result.stdout)
        reference = (journey.parent / "prompt-distance.txt").read_text()
        self.assertIn("refine-1=+1.0000", reference)

    def test_unknown_lesson_and_missing_fence_fail(self):
        journey = self.write(BOARD)
        unknown = run(journey, lesson="nope")
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("unknown lesson: nope", unknown.stderr)
        bare = self.write("# refine-1: Bare\n\nNo fence here.\n")
        missing = run(bare, lesson="refine-1")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("no prompt for refine-1", missing.stderr)
        absent = self.write("# refine-3: Missing\n\nNo fence here either.\n")
        no_prompt = run(absent, lesson="refine-3")
        self.assertEqual(no_prompt.returncode, 1)
        self.assertIn("no prompt for refine-3", no_prompt.stderr)

    def test_identical_texts_are_similarity_one_without_a_service(self):
        journey = self.write(BOARD.replace("beta", "alpha").replace("gamma", "alpha"))
        result = run(journey)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("next=+1.0000", result.stdout.splitlines()[0])

    def test_real_journey_one_lesson_does_not_edit_or_segment(self):
        before = JOURNEY.read_text()
        result = subprocess.run(
            ["just", "prompt-distance", "refine-1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [result.stdout.strip()])
        self.assertTrue(result.stdout.startswith("refine-1"))
        self.assertIn("previous= absent", result.stdout)
        self.assertRegex(result.stdout, r"next=[+-]\d\.\d{4}")
        self.assertIn("next=", result.stdout)
        self.assertNotIn("segment", result.stdout)
        self.assertEqual(JOURNEY.read_text(), before)

    def write(self, text):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = directory / "JOURNEY.md"
        path.write_text(text)
        return path


if __name__ == "__main__":
    unittest.main()
