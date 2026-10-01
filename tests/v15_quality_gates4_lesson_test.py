"""outer.v15.M5b — quality-gates-4 must be startable, carry real debt, and use a working command."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "workshop" / "material" / "quality-gates-4"
APP = ROOT / "app"
TOOL = APP / "scripts" / "check-redundancies"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"


def recipe(justfile: Path) -> str:
    text = justfile.read_text(encoding="utf-8")
    return text[text.index("# Copy/paste redundancy gate") :]


class QualityGates4Lesson(unittest.TestCase):
    def test_lesson_has_one_prompt_and_the_run_block(self):
        text = JOURNEY.read_text(encoding="utf-8")
        section = text[text.index("# quality-gates-4:") :]
        self.assertEqual(section.count("*PROMPT TO TEST*"), 1)
        self.assertIn("just prepare quality-gates-4", section)
        self.assertIn("just claude", section)

    def test_harness_registers_the_lesson(self):
        self.assertIn("_delta-quality-gates-4:", (ROOT / "justfile").read_text(encoding="utf-8"))
        self.assertIn('"quality-gates-4"', (ROOT / "scripts" / "lesson-forks").read_text(encoding="utf-8"))
        self.assertIn('"quality-gates-4"', (ROOT / "scripts" / "lesson-status").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "workshop" / "results" / "quality-gates-4" / "JUDGE.md").is_file())

    def test_the_material_carries_the_debt_the_lesson_describes(self):
        report = Path(tempfile.mkdtemp()) / "r.json"
        # Same tool as the material's (asserted identical below), run from the app so no build lands in material/.
        result = subprocess.run(
            [str(TOOL), str(MATERIAL / "src"), "--fail-on-findings", "--report", str(report)],
            capture_output=True,
            text=True,
            cwd=APP,
        )
        self.assertEqual(result.returncode, 1, "material must start with at least one duplicate")
        self.assertRegex(result.stdout, r"findings: [1-9]")

    def test_material_ships_the_same_pmd_tool_as_the_app(self):
        material_tool = MATERIAL / "scripts" / "check-redundancies"
        self.assertEqual(material_tool.read_text(), TOOL.read_text())
        self.assertTrue(os.access(material_tool, os.X_OK))
        for rel in ("build.sbt", "project/build.properties", ".gitignore", "src/main/scala/CheckRedundancies.scala"):
            self.assertEqual(
                (MATERIAL / "scripts" / "check-redundancies-cpd" / rel).read_text(),
                (APP / "scripts" / "check-redundancies-cpd" / rel).read_text(),
                rel,
            )

    def test_material_recipe_is_the_apps_recipe(self):
        self.assertEqual(recipe(MATERIAL / "justfile"), recipe(APP / "justfile"))

    def test_recipe_accepts_the_prompts_own_command(self):
        prompt = re.search(r"just check-redundancies (--\S+)", JOURNEY.read_text(encoding="utf-8"))
        self.assertIsNotNone(prompt)
        flag = prompt.group(1)
        report = Path(tempfile.mkdtemp()) / "r.json"
        # The app source is quiet, so the exact spelling from the prompt must exit 0, not with a usage error.
        result = subprocess.run(
            ["just", "check-redundancies", flag, f"report={report}"],
            cwd=APP,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report.is_file())

    def test_a_participant_can_start_the_lesson(self):
        work = Path(tempfile.mkdtemp()) / "sandbox"
        record = Path(tempfile.mkdtemp()) / "record"
        env = dict(os.environ, PREPARE_WORK=str(work), PREPARE_RECORD=str(record))
        result = subprocess.run(
            ["just", "prepare", "quality-gates-4"], cwd=ROOT, capture_output=True, text=True, env=env
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("*PROMPT TO TEST*", result.stdout)
        self.assertTrue(os.access(work / "scripts" / "check-redundancies", os.X_OK))
        self.assertTrue((work / "scripts" / "check-redundancies-cpd" / "build.sbt").is_file())
        self.assertTrue((work / "src" / "main" / "scala" / "todo" / "core" / "Todos.scala").is_file())
        self.assertEqual(record.read_text().strip(), "quality-gates-4")
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
