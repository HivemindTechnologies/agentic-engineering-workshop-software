import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
MATERIAL = ROOT / "workshop" / "material"
WOW = MATERIAL / "refine-4" / "docs" / "rules" / "WOW.md"
JUDGE = ROOT / "workshop" / "results" / "refine-1" / "JUDGE.md"
LIBRARY = "org.virtuslab::scala-yaml"
FORBIDDEN = ("circe-yaml", "SnakeYAML", "snakeyaml")


class YamlLibrary(unittest.TestCase):
    def test_refine_1_names_the_library_and_the_store_file(self):
        section = lesson(JOURNEY.read_text(), "refine-1")
        prompt = fenced(section, "*PROMPT TO TEST*")
        self.assertIn(LIBRARY, prompt)
        self.assertIn("todos.yaml", prompt)
        observations = bullets(section)
        self.assertTrue(any(LIBRARY in line and "todos.yaml" in line and "states" in line for line in observations))

    def test_wow_stack_names_only_this_library(self):
        stack = wow_stack(WOW.read_text())
        self.assertIn(LIBRARY, stack)
        for name in FORBIDDEN:
            self.assertNotIn(name, stack)
        self.assertNotIn("circe", stack)

    def test_journey_and_material_name_no_other_yaml_library(self):
        texts = [(JOURNEY, JOURNEY.read_text())]
        for path in MATERIAL.rglob("*"):
            if path.is_file():
                texts.append((path, path.read_text()))
        for path, text in texts:
            for name in FORBIDDEN:
                self.assertNotIn(name, text, str(path.relative_to(ROOT)))
            for line in text.splitlines():
                if "scala-yaml" in line:
                    self.assertIn("org.virtuslab", line, f"{path.relative_to(ROOT)}: {line}")

    def test_refine_1_judge_requires_the_library_and_the_store_file(self):
        text = JUDGE.read_text()
        self.assertIn(LIBRARY, text)
        self.assertIn("todos.yaml", text)
        self.assertIn("todo.yaml", (ROOT / "workshop/results/refine-1/2026-09-28-16-15-10/docs/specs/SPEC.v1-todo-list-cli-mvp.md").read_text())


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


def wow_stack(text):
    lines = text.splitlines()
    start = lines.index("## Stack")
    end = next(index for index in range(start + 1, len(lines)) if lines[index].startswith("## "))
    return "\n".join(lines[start:end])
