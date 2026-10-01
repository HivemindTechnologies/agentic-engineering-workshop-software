import importlib.machinery
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "instruct"
SPEC = "docs/specs/SPEC.v1-todo-list-cli-mvp.md"

TWO = """# refine-1: First

*PROMPT TO TEST*
```
alpha
```

*EXPECTED OBSERVATIONS*
- stays small

# refine-1a: Second

*PROMPT TO TEST*
```
beta
```

*EXPECTED OBSERVATIONS*
- still small

Follow-up: what broke?
"""

VECTORS = {"refine-1": [1, 0], "refine-1a": [0, 1]}

BOARD = "\n".join(
    [
        "refine-1     previous= absent next=+0.0000",
        "refine-1a    previous=+0.0000 next= absent",
        "segment refine-1 refine-1a",
    ]
)


def load_instruct():
    loader = importlib.machinery.SourceFileLoader("instruct_script", str(SCRIPT))
    spec = importlib.util.spec_from_loader("instruct_script", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def run(directory, lesson="", vectors=None):
    args = [str(SCRIPT), str(directory / "JOURNEY.md"), str(directory / "results")]
    if lesson:
        args += ["--lesson", lesson]
    if vectors is not None:
        path = directory / "vectors.json"
        path.write_text(json.dumps(vectors))
        args += ["--vectors", str(path)]
    return subprocess.run(args, capture_output=True, text=True)


class Instruct(unittest.TestCase):
    def test_unjudged_lessons_are_not_a_failure_and_a_low_similarity_is_not_either(self):
        directory = self.layout(TWO)
        before = (directory / "JOURNEY.md").read_text()
        result = run(directory, vectors=VECTORS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(BOARD + "\n"), result.stdout)
        self.assertEqual(result.stdout.count("segment "), 1)
        self.assertIn("refine-1 not yet judged", result.stdout)
        self.assertIn("refine-1a not yet judged", result.stdout)
        self.assertIn("refine-1     previous= absent next=+0.0000", result.stdout)
        self.assertIn("refine-1a    previous=+0.0000 next= absent", result.stdout)
        self.assertNotIn("TOC correction", result.stdout)
        journey = (directory / "JOURNEY.md").read_text()
        self.assertIn("# refine-1: First (last: not run)\n", journey)
        self.assertIn("# refine-1a: Second (last: not run)\n", journey)
        self.assertIn("Follow-up: what broke?", journey)
        self.assertEqual(self.body(journey, "refine-1a"), self.body(before, "refine-1a"))
        self.assertEqual((directory / "develop" / "sentinel").read_text(), "keep")
        source = SCRIPT.read_text()
        self.assertIn("prompt-distance", source)
        self.assertNotIn("cosine", source)
        self.assertNotIn("sha256", source)
        self.assertNotIn("claude", source)
        self.assertNotIn("develop", source)

    def test_one_lesson_shows_its_line_refreshes_its_mark_and_leaves_a_smooth_lesson(self):
        directory = self.layout(TWO)
        self.judge(directory, "refine-1a", "pass")
        before_body = self.body((directory / "JOURNEY.md").read_text(), "refine-1a")
        result = run(directory, lesson="refine-1a", vectors=VECTORS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("segment", result.stdout)
        self.assertNotIn("refine-1 not yet judged", result.stdout)
        self.assertEqual(
            result.stdout,
            "refine-1a    previous=+0.0000 next= absent\nrefine-1a smooth\n",
        )
        journey = (directory / "JOURNEY.md").read_text()
        self.assertIn("# refine-1: First\n", journey)
        self.assertNotIn("# refine-1: First (last:", journey)
        self.assertIn("# refine-1a: Second (last: not run)\n", journey)
        self.assertEqual(self.body(journey, "refine-1a"), before_body)
        self.assertEqual(self.body(journey, "refine-1"), self.body(TWO, "refine-1"))

    def test_a_failing_judgement_leaves_the_section_and_does_not_stop_the_rest(self):
        directory = self.layout(TWO)
        self.passing_tree(directory, "refine-1")
        self.judge(directory, "refine-1", "fail")
        before = (directory / "JOURNEY.md").read_text()
        result = run(directory, vectors=VECTORS)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("refine-1 left unchanged: newest judgement is verdict: fail", result.stdout)
        self.assertIn("refine-1a not yet judged", result.stdout)
        journey = (directory / "JOURNEY.md").read_text()
        self.assertIn("# refine-1: First (last: FAIL judge 2026-09-28-02-00-00)\n", journey)
        self.assertEqual(self.body(journey, "refine-1"), self.body(before, "refine-1"))
        self.assertEqual(self.body(journey, "refine-1a"), self.body(before, "refine-1a"))
        self.assertNotIn("# refine-1a: Second (last: FAIL", journey)

    def test_a_stale_pass_mark_is_refreshed_before_the_lesson_is_treated_as_smooth(self):
        text = TWO.replace("# refine-1: First", "# refine-1: First (last: PASS)")
        directory = self.layout(text)
        self.passing_tree(directory, "refine-1")
        self.judge(directory, "refine-1", "fail")
        result = run(directory, lesson="refine-1", vectors=VECTORS)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refine-1 left unchanged: newest judgement is verdict: fail", result.stdout)
        journey = (directory / "JOURNEY.md").read_text()
        self.assertIn("# refine-1: First (last: FAIL judge 2026-09-28-02-00-00)\n", journey)
        self.assertEqual(journey.count("(last:"), 1)

    def test_a_passing_refine_5_is_smooth_and_marked_pass(self):
        journey = """# refine-5: Later

*PROMPT TO TEST*
```
gamma
```

*EXPECTED OBSERVATIONS*
- one observation
"""
        directory = self.layout(journey)
        self.passing_tree(directory, "refine-5")
        self.judge(directory, "refine-5", "pass")
        result = run(directory, lesson="refine-5", vectors={"refine-5": [1, 0]})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("refine-5 smooth", result.stdout)
        text = (directory / "JOURNEY.md").read_text()
        self.assertIn("# refine-5: Later (last: PASS 2026-09-28-02-00-00)\n", text)
        self.assertTrue(text.splitlines()[0].startswith("# refine-5:"))

    def test_no_passing_judgement_is_not_smooth(self):
        directory = self.layout(TWO)
        (directory / "results" / "refine-1" / "JUDGE.md").parent.mkdir(parents=True)
        (directory / "results" / "refine-1" / "JUDGE.md").write_text("judge the observation\n")
        result = run(directory, lesson="refine-1", vectors=VECTORS)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refine-1 left unchanged: no passing judgement", result.stdout)
        self.assertIn("# refine-1: First (last: not run)\n", (directory / "JOURNEY.md").read_text())

    def test_a_second_prompt_block_fails_before_any_edit(self):
        journey = TWO.replace(
            "*EXPECTED OBSERVATIONS*\n- stays small",
            "*PROMPT TO TEST*\n```\nsecond\n```\n\n*EXPECTED OBSERVATIONS*\n- stays small",
        )
        directory = self.layout(journey)
        before = (directory / "JOURNEY.md").read_text()
        result = run(directory, lesson="refine-1", vectors=VECTORS)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refine-1 has 2 prompts", result.stderr)
        self.assertEqual((directory / "JOURNEY.md").read_text(), before)

    def test_unknown_lesson_fails(self):
        directory = self.layout(TWO)
        result = run(directory, lesson="nope")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown lesson: nope", result.stderr)

    def test_a_headline_change_is_printed_as_a_toc_correction(self):
        module = load_instruct()
        before = "# refine-1: Old\n# refine-1a: Next\n"
        after = "# refine-1a: Next\n# refine-1: New (last: PASS)\n"
        self.assertEqual(
            module.toc_corrections(before, after),
            [
                "TOC correction: order refine-1 refine-1a -> refine-1a refine-1",
                "TOC correction: # refine-1: Old -> # refine-1: New",
            ],
        )
        marked = "# refine-1: Old (last: not run)\n"
        self.assertEqual(module.toc_corrections("# refine-1: Old\n", marked), [])
        self.assertIn("toc_corrections(", SCRIPT.read_text())

    def test_the_just_recipe_stays_in_the_outer_repository(self):
        shown = subprocess.run(["just", "--show", "instruct"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("scripts/instruct", shown.stdout)
        self.assertNotIn("prepare", shown.stdout)
        self.assertNotIn("claude", shown.stdout)
        self.assertNotIn("judge", shown.stdout)
        self.assertNotIn("instructor.md", shown.stdout)

    def layout(self, journey):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (directory / "JOURNEY.md").write_text(journey)
        (directory / "results").mkdir()
        develop = directory / "develop"
        develop.mkdir()
        (develop / "sentinel").write_text("keep")
        return directory

    def judge(self, directory, lesson, word):
        lesson_dir = directory / "results" / lesson
        (lesson_dir / "judgements").mkdir(parents=True, exist_ok=True)
        (lesson_dir / "JUDGE.md").write_text("decide the observations\n")
        (lesson_dir / "judgements" / "2026-09-28-03-00-00.md").write_text(f"notes\nverdict: {word}\n")

    def passing_tree(self, directory, lesson):
        lesson_dir = directory / "results" / lesson
        lesson_dir.mkdir(parents=True, exist_ok=True)
        (lesson_dir / "cutoff").write_text("2026-09-28-01-00-00\n")
        spec = lesson_dir / "2026-09-28-02-00-00" / SPEC
        spec.parent.mkdir(parents=True)
        spec.write_text("# spec\n")
        (spec.parent / "session.jsonl").write_text(
            json.dumps({"type": "result", "num_turns": 1, "usage": {"input_tokens": 1}}) + "\n"
        )

    def body(self, text, lesson):
        lines = text.splitlines()
        start = next(index for index, line in enumerate(lines) if line.startswith(f"# {lesson}:"))
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if lines[index].startswith("# "):
                end = index
                break
        content = lines[start + 1 : end]
        while content and (
            content[0].startswith("Minimum Runtime: ")
            or content[0].startswith("Last Token Usage: ")
            or content[0].startswith("[Results](")
            or content[0].startswith("[Material](")
            or content[0].startswith("[develop](")
        ):
            content = content[1:]
        return "\n".join(content)


if __name__ == "__main__":
    unittest.main()
