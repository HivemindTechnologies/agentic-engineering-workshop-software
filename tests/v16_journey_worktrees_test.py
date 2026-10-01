"""outer.v16 — worktrees, explore commands, lesson-bound milestone ids."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
WORKTREES = ROOT / "scripts" / "journey-worktrees"
ORDER = ROOT / "scripts" / "lesson-order"
SPEC = ROOT / "docs" / "specs" / "SPEC.v16-journey-worktrees-and-explore.md"
REFINE = ROOT / ".claude" / "skills" / "refine" / "SKILL.md"
CHECK = ROOT / "scripts" / "spec-check"

EXPLORE_LESSONS = (
    "implement-1",
    "implement-1b",
    "implement-2",
    "quality-gates-1",
    "quality-gates-2",
    "quality-gates-3",
    "quality-gates-4",
)


def lesson_section(text: str, lesson: str) -> str:
    m = re.search(rf"(?ms)^# {re.escape(lesson)}:.*?(?=^# [a-z0-9-]+:|\Z)", text)
    assert m, f"missing lesson {lesson}"
    return m.group(0)


class JourneyWorktrees(unittest.TestCase):
    def test_script_and_recipe_exist(self):
        self.assertTrue(WORKTREES.is_file())
        just = (ROOT / "justfile").read_text(encoding="utf-8")
        self.assertRegex(just, r"(?m)^journey-worktrees")

    def test_fixture_summary_is_two_layers(self):
        import runpy

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "specs").mkdir(parents=True)
            (root / "docs" / "specs" / "SPEC.md").write_text("x\n")
            (root / "src" / "main" / "scala" / "todo").mkdir(parents=True)
            (root / "src" / "main" / "scala" / "todo" / "Cli.scala").write_text("x\n")
            (root / "README.md").write_text("hi\n")
            (root / "target" / "deep").mkdir(parents=True)
            (root / "target" / "deep" / "x.class").write_text("x\n")
            mod = runpy.run_path(str(WORKTREES))
            lines = mod["summarize"](root)
            joined = "\n".join(lines)
            self.assertIn("docs/", joined)
            self.assertIn("specs/", joined)
            self.assertNotIn("SPEC.md", joined)  # third layer omitted
            self.assertNotIn("target", joined)
            self.assertNotIn("Cli.scala", joined)

    def test_live_journey_has_one_worktree_per_lesson(self):
        order = subprocess.check_output([str(ORDER), str(JOURNEY)], text=True).split()
        text = JOURNEY.read_text(encoding="utf-8")
        self.assertEqual(text.count("*WORKTREE*"), len(order))
        for lesson in order:
            sec = lesson_section(text, lesson)
            self.assertEqual(sec.count("*WORKTREE*"), 1, lesson)
            self.assertIn("```", sec)

    def test_refresh_is_idempotent(self):
        first = subprocess.check_output(["python3", str(WORKTREES)], text=True)
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".md") as fh:
            fh.write(first)
            path = Path(fh.name)
        second = subprocess.check_output(
            ["python3", str(WORKTREES), "--journey", str(path)], text=True
        )
        self.assertEqual(first, second)


class JourneyExplore(unittest.TestCase):
    def test_explore_blocks_for_target_lessons(self):
        text = JOURNEY.read_text(encoding="utf-8")
        for lesson in EXPLORE_LESSONS:
            with self.subTest(lesson=lesson):
                sec = lesson_section(text, lesson)
                self.assertIn("*EXPLORE COMMANDS*", sec)
                self.assertIn("```", sec)

    def test_implement_2_lists(self):
        sec = lesson_section(JOURNEY.read_text(encoding="utf-8"), "implement-2")
        self.assertIn("list", sec.lower())

    def test_quality_gates_1_fail_then_pass(self):
        sec = lesson_section(JOURNEY.read_text(encoding="utf-8"), "quality-gates-1")
        explore = sec[sec.index("*EXPLORE COMMANDS*") :]
        self.assertIn("touch", explore)
        self.assertIn("git add", explore)
        self.assertIn("git commit", explore)
        self.assertTrue("expect fail" in explore.lower() or "fail" in explore.lower())
        self.assertTrue("expect success" in explore.lower() or "success" in explore.lower())
        fence = re.search(r"```sh\n(.*?)```", explore, re.S)
        self.assertIsNotNone(fence)
        lines = [ln for ln in fence.group(1).splitlines() if ln.strip()]
        self.assertLessEqual(len(lines), 8)

    def test_quality_gates_3_and_4_tokens(self):
        text = JOURNEY.read_text(encoding="utf-8")
        self.assertIn("spec-check", lesson_section(text, "quality-gates-3"))
        qg4 = lesson_section(text, "quality-gates-4")
        self.assertTrue("check-redundancies" in qg4 or "redundan" in qg4.lower())


class SpecCheckLessonIds(unittest.TestCase):
    def test_v16_uses_hyphenated_ids_and_refine_docs(self):
        spec = SPEC.read_text(encoding="utf-8")
        self.assertIn("## M2-implement-1:", spec)
        self.assertIn("## M2-quality-gates-1:", spec)
        self.assertNotIn("## M2implement-1:", spec)
        refine = REFINE.read_text(encoding="utf-8")
        self.assertIn("M2-implement-1", refine)
        self.assertIn("v16.M2-implement-1", refine)
        result = subprocess.run([str(CHECK), str(SPEC)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
