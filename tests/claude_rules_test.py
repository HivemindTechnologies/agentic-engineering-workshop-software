import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIAL = ROOT / "workshop" / "material"
RESULTS = ROOT / "workshop" / "results"
SENTENCE = "A command-line todo list in Scala 3. Pure functional core, Cats Effect at the edge, one YAML file as the store."
PARAPHRASE = "pure FP, fail fast, illegal states unrepresentable, outcomes in the return type, TDD, no mocks."


class ClaudeRules(unittest.TestCase):
    def test_claude_md_names_wow_without_restating_it(self):
        claudes = sorted(MATERIAL.rglob("CLAUDE.md"))
        self.assertEqual([path.relative_to(MATERIAL).parts[0] for path in claudes], ["00-base", "refine-5", "refine-7"])
        for path in claudes:
            self.assertNotIn(SENTENCE, path.read_text(), str(path.relative_to(ROOT)))
        base = (MATERIAL / "00-base" / "CLAUDE.md").read_text()
        self.assertNotIn("docs/rules/WOW.md", base)
        for name in ("refine-5", "refine-7"):
            text = (MATERIAL / name / "CLAUDE.md").read_text()
            self.assertIn("docs/rules/WOW.md", text)
            self.assertIn("binding", text)
            self.assertNotIn(PARAPHRASE, text)
        for path in sorted(RESULTS.glob("*/JUDGE.md")):
            text = path.read_text()
            self.assertNotIn(SENTENCE, text, str(path.relative_to(ROOT)))
            self.assertNotIn(PARAPHRASE, text, str(path.relative_to(ROOT)))
