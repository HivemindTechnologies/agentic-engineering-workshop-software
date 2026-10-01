import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "term-drift"
JUSTFILE = ROOT / "justfile"
REPRODUCTION = ROOT / "workshop" / "term-drift-reproduction.txt"


class TermDrift(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.journey = self.tmp / "JOURNEY.md"
        self.material = self.tmp / "material"
        self.material.mkdir()
        self.natural = self.tmp / "natural.txt"
        self.pinned = self.tmp / "pinned.txt"

    def test_a_natural_plural_exits_zero_and_a_second_run_matches(self):
        self.journey.write_text(lesson("refine-1", "keep the file", ["files stay"]))
        self.natural.write_text("file files\n")
        self.pinned.write_text("")
        first = self.drift()
        second = self.drift()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, "file refine-1 files refine-1 plural 1\n")
        self.assertEqual(second.stdout, first.stdout)
        self.assertEqual(second.returncode, 0)

    def test_a_pinned_edit_exits_nonzero_and_names_both_tokens(self):
        self.journey.write_text(lesson("refine-1", "the store is todo.yaml", []))
        (self.material / "spec.md").write_text("the store is todos.yaml\n")
        self.natural.write_text("")
        self.pinned.write_text("todo.yaml todos.yaml\n")
        result = self.drift()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "todo.yaml refine-1 todos.yaml spec.md edit 1\n")
        self.assertIn("todo.yaml", result.stdout)
        self.assertIn("todos.yaml", result.stdout)

    def test_store_and_database_print_no_cluster(self):
        self.journey.write_text(lesson("refine-1", "store and database", []))
        self.natural.write_text("")
        self.pinned.write_text("")
        result = self.drift()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_an_unlisted_cosine_cluster_exits_nonzero(self):
        self.journey.write_text(lesson("refine-1", "aaaaaaabcde versus aaaaaaawxyz", []))
        self.natural.write_text("")
        self.pinned.write_text("")
        result = self.drift()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "aaaaaaabcde refine-1 aaaaaaawxyz refine-1 cosine +0.8621\n")

    def test_stopwords_and_short_tokens_are_dropped(self):
        self.journey.write_text(lesson("refine-1", "that cat thats cats", []))
        self.natural.write_text("")
        self.pinned.write_text("")
        result = self.drift()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_recipe_reads_the_three_sources_and_the_two_lists(self):
        text = JUSTFILE.read_text()
        recipe = text.split("term-drift:", 1)[1].split("\n\n", 1)[0]
        self.assertIn("scripts/term-drift", recipe)
        self.assertIn("workshop/JOURNEY.md", recipe)
        self.assertIn("workshop/material", recipe)
        self.assertIn("workshop/term-drift-natural.txt", recipe)
        self.assertIn("workshop/term-drift-pinned.txt", recipe)
        self.assertNotIn("workshop/results", recipe)
        self.assertNotIn("develop/", recipe)
        self.assertNotIn("claude", recipe)

    def test_the_first_run_keeps_the_store_pair(self):
        historical = [
            line
            for line in REPRODUCTION.read_text().splitlines()
            if "todo.yaml" in line.split() and "todos.yaml" in line.split()
        ]
        self.assertEqual(
            historical,
            ["todo.yaml refine-1 todos.yaml implement-1b/docs/specs/SPEC.v1-todo-list-cli-mvp.md edit 1"],
        )


    def drift(self):
        return subprocess.run(
            ["python3", str(SCRIPT), str(self.journey), str(self.material), str(self.natural), str(self.pinned)],
            capture_output=True,
            text=True,
        )

def lesson(name, prompt, observations):
    bullets = "\n".join(f"- {item}" for item in observations)
    block = f"*EXPECTED OBSERVATIONS*\n{bullets}\n" if observations else ""
    return f"# {name}: Title\n\n*PROMPT TO TEST*\n```\n{prompt}\n```\n\n{block}"
