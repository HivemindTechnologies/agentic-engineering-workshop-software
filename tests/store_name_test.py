import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
MATERIAL = ROOT / "workshop" / "material"
RESULTS = ROOT / "workshop" / "results"
SCRIPT = ROOT / "scripts" / "term-drift"
PINNED = ROOT / "workshop" / "term-drift-pinned.txt"
KEPT_JUDGEMENT = RESULTS / "refine-1" / "judgements" / "2026-09-28-16-15-32.md"
KEPT_TREE = RESULTS / "refine-1" / "2026-09-28-16-15-10" / "docs" / "specs" / "SPEC.v1-todo-list-cli-mvp.md"


class StoreName(unittest.TestCase):
    def test_journey_and_material_name_todos_yaml_and_not_todo_yaml(self):
        journey = JOURNEY.read_text()
        self.assertIn("todos.yaml", journey)
        self.assertNotIn("todo.yaml", journey)
        material_hits = []
        for path in MATERIAL.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text()
            self.assertNotIn("todo.yaml", text, str(path.relative_to(ROOT)))
            if "todos.yaml" in text:
                material_hits.append(path)
        self.assertTrue(material_hits)

    def test_judges_that_name_the_store_name_todos_yaml(self):
        named = []
        for path in sorted(RESULTS.glob("*/JUDGE.md")):
            text = path.read_text()
            self.assertNotIn("todo.yaml", text, str(path.relative_to(ROOT)))
            if "store file" in text:
                self.assertIn("todos.yaml", text, str(path.relative_to(ROOT)))
                named.append(path)
        self.assertEqual(
            [path.parent.name for path in named],
            ["refine-1", "refine-1a", "refine-2"],
        )

    def test_a_prompt_that_does_not_mention_the_store_stays(self):
        self.assertIn("*PROMPT TO TEST*\n```\n/implement M1\n```", JOURNEY.read_text())

    def test_stamped_trees_and_judgements_still_say_todo_yaml(self):
        self.assertIn("todo.yaml", KEPT_JUDGEMENT.read_text())
        self.assertIn("todo.yaml", KEPT_TREE.read_text())

    def test_term_drift_no_longer_reports_the_pair_and_the_pin_stays(self):
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                str(JOURNEY),
                str(MATERIAL),
                str(ROOT / "workshop" / "term-drift-natural.txt"),
                str(PINNED),
            ],
            capture_output=True,
            text=True,
        )
        reported = [
            line
            for line in result.stdout.splitlines()
            if "todo.yaml" in line.split() and "todos.yaml" in line.split()
        ]
        self.assertEqual(reported, [])
        self.assertEqual(PINNED.read_text(), "todo.yaml todos.yaml\n")
        self.assertNotIn("claude", result.stderr)
