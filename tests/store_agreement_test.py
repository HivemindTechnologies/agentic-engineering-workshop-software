import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
MATERIAL = ROOT / "workshop" / "material"
RESULTS = ROOT / "workshop" / "results"
SPEC = MATERIAL / "refine-6" / "docs" / "specs" / "SPEC.v1-todo-list-cli-mvp.md"
IMPLEMENT_1 = MATERIAL / "implement-1"
KEPT_TREE = RESULTS / "refine-1" / "2026-09-28-16-15-10" / "docs" / "specs" / "SPEC.v1-todo-list-cli-mvp.md"
LESSONS = ("refine-1", "refine-1a", "refine-2", "refine-3", "refine-4", "refine-5")


class StoreAgreement(unittest.TestCase):
    def test_prompts_and_the_refine_6_spec_name_todos_yaml(self):
        text = JOURNEY.read_text()
        named = []
        for name in LESSONS:
            prompt = fenced(lesson(text, name), "*PROMPT TO TEST*")
            self.assertNotIn("todo.yaml", prompt, name)
            if "todos.yaml" in prompt or "todo.yaml" in prompt:
                self.assertIn("todos.yaml", prompt, name)
                named.append(name)
        self.assertIn("refine-1", named)
        observations = bullets(lesson(text, "refine-1"))
        self.assertTrue(any("todos.yaml" in line for line in observations))
        spec = SPEC.read_text()
        self.assertIn("todos.yaml", spec)
        self.assertNotIn("todo.yaml", spec)
        implement_files = [path for path in IMPLEMENT_1.rglob("*") if path.is_file()]
        self.assertTrue(implement_files)
        for path in implement_files:
            self.assertNotIn("todo.yaml", path.read_text(), str(path.relative_to(ROOT)))
        for name in LESSONS:
            judge = RESULTS / name / "JUDGE.md"
            judge_text = judge.read_text()
            self.assertNotIn("todo.yaml", judge_text, name)
            if "store file" in judge_text:
                self.assertIn("todos.yaml", judge_text, name)
        self.assertIn("todo.yaml", KEPT_TREE.read_text())


def lesson(text, name):
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(f"# {name}:"))
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("# ")), len(lines))
    return lines[start:end]


def fenced(lines, marker):
    start = lines.index(marker)
    opener = next(index for index in range(start + 1, len(lines)) if lines[index].startswith("```"))
    closer = next(index for index in range(opener + 1, len(lines)) if lines[index].startswith("```"))
    return "\n".join(lines[opener + 1 : closer])


def bullets(lines):
    start = lines.index("*EXPECTED OBSERVATIONS*")
    found = []
    for line in lines[start + 1 :]:
        if line.startswith("- "):
            found.append(line[2:])
        elif line.strip() == "":
            continue
        else:
            break
    return found
