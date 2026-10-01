import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "judge-given"
MATERIAL = ROOT / "workshop" / "material"


def run(material, lesson, paths=False):
    args = [str(SCRIPT), str(material), lesson]
    if paths:
        args.append("--paths")
    return subprocess.run(args, capture_output=True, text=True)


class JudgeGiven(unittest.TestCase):
    def test_a_later_delta_replaces_a_shared_path_and_a_later_lesson_is_excluded(self):
        workshop = Path(self.enterContext(tempfile.TemporaryDirectory()))
        material = workshop / "material"
        (workshop / "JOURNEY.md").write_text(
            "\n".join(
                f"# {name}: Title\n"
                for name in (
                    "refine-1",
                    "refine-1a",
                    "refine-2",
                    "refine-3",
                    "refine-4",
                    "refine-5",
                )
            )
            + "\n"
        )
        self.write(material / "00-base" / "justfile", "base just\n")
        self.write(material / "00-base" / "CLAUDE.md", "base claude\n")
        self.write(material / "refine-1a" / "CLAUDE.md", "first claude\n")
        self.write(material / "refine-1a" / ".claude" / "commands" / "refine.md", "refine\n")
        self.write(material / "refine-4" / "CLAUDE.md", "second claude\n")
        self.write(material / "refine-4" / "docs" / "rules" / "WOW.md", "wow\n")
        self.write(material / "refine-5" / "docs" / "rules" / "EXTRA.md", "after\n")
        result = run(material, "refine-4")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("# Given to the participant\n"))
        self.assertIn("## justfile\n```\nbase just\n```", result.stdout)
        self.assertIn("## CLAUDE.md\n```\nsecond claude\n```", result.stdout)
        self.assertNotIn("base claude", result.stdout)
        self.assertNotIn("first claude", result.stdout)
        self.assertIn("## docs/rules/WOW.md\n```\nwow\n```", result.stdout)
        self.assertNotIn("EXTRA.md", result.stdout)
        self.assertNotIn("after", result.stdout)
        paths = run(material, "refine-4", paths=True)
        self.assertEqual(paths.returncode, 0, paths.stderr)
        self.assertEqual(
            paths.stdout.splitlines(),
            [".claude/commands/refine.md", "CLAUDE.md", "docs/rules/WOW.md", "justfile"],
        )
        self.assertNotIn("```", paths.stdout)

    def test_refine_4_is_given_wow_and_refine_1_is_not(self):
        refine_4 = run(MATERIAL, "refine-4")
        self.assertEqual(refine_4.returncode, 0, refine_4.stderr)
        self.assertIn("## docs/rules/WOW.md", refine_4.stdout)
        self.assertIn("Option` and `Either` for expected failure", refine_4.stdout)
        self.assertIn("## .claude/commands/refine.md", refine_4.stdout)
        self.assertIn("## justfile", refine_4.stdout)
        self.assertNotIn("Read `docs/rules/WOW.md` before writing", refine_4.stdout)
        refine_1 = run(MATERIAL, "refine-1")
        self.assertEqual(refine_1.returncode, 0, refine_1.stderr)
        self.assertNotIn("WOW.md", refine_1.stdout)
        self.assertNotIn(".claude/commands/refine.md", refine_1.stdout)
        refine_5 = run(MATERIAL, "refine-5")
        self.assertIn("Read `docs/rules/WOW.md` before writing", refine_5.stdout)
        self.assertIn("## docs/rules/WOW.md", refine_5.stdout)

    def test_the_prompt_drops_the_repeated_rule_and_the_judge_can_read_result_trees(self):
        journey = (ROOT / "workshop" / "JOURNEY.md").read_text()
        section = journey.split("# refine-4:", 1)[1].split("# refine-5:", 1)[0]
        self.assertNotIn("Expected failure is Option or Either", section)
        judge = (ROOT / "workshop" / "results" / "refine-4" / "JUDGE.md").read_text()
        self.assertIn("docs/rules/WOW.md", judge)
        self.assertIn("cites", judge)
        justfile = (ROOT / "justfile").read_text()
        self.assertIn("scripts/judge-given", justfile)
        start = justfile.index("judge lesson")
        end = justfile.index("\n# One line per lesson", start)
        block = justfile[start:end]
        self.assertNotIn("--tools", block)
        self.assertIn("--allow \"$results\"", block)
        self.assertIn("given:", justfile)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


if __name__ == "__main__":
    unittest.main()
