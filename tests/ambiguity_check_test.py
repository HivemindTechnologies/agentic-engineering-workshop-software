import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ambiguity-check"
JUSTFILE = ROOT / "justfile"
REGISTRY = ROOT / "workshop" / "known-ambiguities.txt"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
MATERIAL = ROOT / "workshop" / "material"


def lesson(name, prompt, observations=()):
    bullets = "\n".join(f"- {item}" for item in observations)
    block = f"*EXPECTED OBSERVATIONS*\n{bullets}\n" if observations else ""
    return f"# {name}: Title\n\n*PROMPT TO TEST*\n```\n{prompt}\n```\n\n{block}"


class AmbiguityCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.journey = self.tmp / "JOURNEY.md"
        self.material = self.tmp / "material"
        self.material.mkdir()
        self.registry = self.tmp / "registry.txt"

    def check(self):
        return subprocess.run(
            [str(SCRIPT), str(self.journey), str(self.material), str(self.registry)],
            capture_output=True,
            text=True,
        )

    def test_a_satisfied_require_exits_zero(self):
        self.journey.write_text(lesson("skills-1", "each as .claude/skills/<name>/SKILL.md"))
        self.registry.write_text(
            "lesson: skills-1\n"
            "require: .claude/skills/<name>/SKILL.md\n"
            "why: a flat file is not auto-discovered as a skill\n"
        )
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_reverted_require_fails_and_names_the_entry(self):
        self.journey.write_text(lesson("skills-1", "make the claude commands into skills"))
        self.registry.write_text(
            "lesson: skills-1\n"
            "require: .claude/skills/<name>/SKILL.md\n"
            "why: a flat file is not auto-discovered as a skill\n"
        )
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skills-1", result.stderr)
        self.assertIn(".claude/skills/<name>/SKILL.md", result.stderr)
        self.assertIn("a flat file is not auto-discovered as a skill", result.stderr)

    def test_forbid_fails_when_the_text_is_present_in_material(self):
        self.journey.write_text(lesson("refine-1", "the store is todos.yaml"))
        (self.material / "refine-1").mkdir()
        (self.material / "refine-1" / "spec.md").write_text("store: todo.yaml\n")
        self.registry.write_text("lesson: refine-1\nforbid: todo.yaml\nwhy: renamed to todos.yaml\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refine-1", result.stderr)

    def test_forbid_passes_when_the_text_is_absent(self):
        self.journey.write_text(lesson("refine-1", "the store is todos.yaml"))
        (self.material / "refine-1").mkdir()
        (self.material / "refine-1" / "spec.md").write_text("store: todos.yaml\n")
        self.registry.write_text("lesson: refine-1\nforbid: todo.yaml\nwhy: renamed to todos.yaml\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_multiple_entries_stop_at_the_first_failure(self):
        self.journey.write_text(
            lesson("refine-1", "alpha bravo") + lesson("refine-2", "charlie delta")
        )
        self.registry.write_text(
            "lesson: refine-1\n"
            "require: missing-text\n"
            "why: first entry fails\n"
            "\n"
            "lesson: refine-2\n"
            "require: also-missing\n"
            "why: second entry, never reached\n"
        )
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("first entry fails", result.stderr)
        self.assertNotIn("second entry, never reached", result.stderr)

    def test_an_unknown_lesson_in_the_registry_is_a_script_error(self):
        self.journey.write_text(lesson("refine-1", "alpha"))
        self.registry.write_text("lesson: nope\nrequire: x\nwhy: y\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nope", result.stderr)

    def test_a_malformed_entry_names_the_line(self):
        self.journey.write_text(lesson("refine-1", "alpha"))
        self.registry.write_text("lesson: refine-1\nwhy: missing require or forbid\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(self.registry), result.stderr)

    def test_recipe_reads_the_three_sources(self):
        text = JUSTFILE.read_text()
        recipe = text.split("ambiguity-check:", 1)[1].split("\n\n", 1)[0]
        self.assertIn("scripts/ambiguity-check", recipe)
        self.assertIn("workshop/JOURNEY.md", recipe)
        self.assertIn("workshop/material", recipe)
        self.assertIn("workshop/known-ambiguities.txt", recipe)
        self.assertNotIn("workshop/results", recipe)
        self.assertNotIn("develop/", recipe)
        self.assertNotIn("claude", recipe)

    def test_the_real_registry_passes_against_the_real_journey_and_material(self):
        result = subprocess.run(
            [str(SCRIPT), str(JOURNEY), str(MATERIAL), str(REGISTRY)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reverting_the_skills_1_prompt_reproduces_the_incident(self):
        reverted = JOURNEY.read_text().replace(
            "make the claude commands /refine and /implement into skills, each as .claude/skills/<name>/SKILL.md, and",
            "make the claude commands /refine and /implement into skills and",
        )
        self.assertNotEqual(reverted, JOURNEY.read_text())
        self.journey.write_text(reverted)
        result = subprocess.run(
            [str(SCRIPT), str(self.journey), str(MATERIAL), str(REGISTRY)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skills-1", result.stderr)


if __name__ == "__main__":
    unittest.main()
