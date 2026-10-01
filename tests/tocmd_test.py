import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "tocmd"


def run(*args):
    return subprocess.run([str(SCRIPT), *args], capture_output=True, text=True)


class Tocmd(unittest.TestCase):
    def test_prints_headings_in_order_without_line_numbers(self):
        path = write(
            self.tmp(),
            "spec.md",
            "\n".join(
                [
                    "# Root",
                    "",
                    "prose",
                    "",
                    "## M1: One (Status: PENDING)",
                    "",
                    "### nested",
                    "",
                    "## M2: Two (Status: PENDING)",
                    "",
                ]
            ),
        )
        result = run(str(path))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "\n".join(
                [
                    "# Root",
                    "## M1: One (Status: PENDING)",
                    "### nested",
                    "## M2: Two (Status: PENDING)",
                    "",
                ]
            ),
        )
        # scala-cli may print compile progress on a cold cache; ignore stderr here.

    def test_lines_flag_prefixes_each_heading_with_its_line_number(self):
        path = write(
            self.tmp(),
            "spec.md",
            "\n".join(
                [
                    "# Root",
                    "",
                    "## M1: One",
                    "",
                ]
            ),
        )
        result = run("--lines", str(path))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "1 # Root\n3 ## M1: One\n")

    def test_a_directory_prints_each_file_labeled_with_a_blank_line_between(self):
        directory = self.tmp()
        first = write(directory, "a.md", "# A\n\n## one\n")
        second = write(directory, "b.md", "# B\n\n## two\n")
        result = run(str(directory))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "\n".join(
                [
                    str(first),
                    "# A",
                    "## one",
                    "",
                    str(second),
                    "# B",
                    "## two",
                    "",
                ]
            ),
        )

    def test_a_single_file_in_a_directory_does_not_print_the_path_label(self):
        directory = self.tmp()
        only = write(directory, "only.md", "# Solo\n")
        result = run(str(only))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "# Solo\n")

    def test_an_empty_directory_exits_non_zero(self):
        directory = self.tmp()
        result = run(str(directory))
        self.assertNotEqual(result.returncode, 0)

    def test_a_missing_file_exits_non_zero(self):
        path = self.tmp() / "missing.md"
        result = run(str(path))
        self.assertNotEqual(result.returncode, 0)

    def test_skills_mention_tocmd(self):
        refine = (ROOT / ".claude" / "skills" / "refine" / "SKILL.md").read_text()
        implement = (ROOT / ".claude" / "skills" / "implement" / "SKILL.md").read_text()
        self.assertIn("scripts/tocmd", refine)
        self.assertIn("--lines", refine)
        self.assertIn("scripts/tocmd --lines", implement)

    def test_compare_equal_outlines_exit_zero(self):
        path = write(self.tmp(), "same.md", "# Root\n\n## One\n")
        result = run("--compare", str(path), str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_compare_differing_outlines_exit_nonzero_with_heading_diff(self):
        directory = self.tmp()
        left = write(directory, "left.md", "# Root\n\n## One\n")
        right = write(directory, "right.md", "# Root\n\n## Two\n")
        result = run("--compare", str(left), str(right))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("---", result.stdout)
        self.assertIn("+++", result.stdout)
        self.assertTrue(
            "## One" in result.stdout and "## Two" in result.stdout,
            result.stdout,
        )

    def test_just_tocmd_recipe_exposes_script(self):
        shown = subprocess.run(
            ["just", "--show", "tocmd"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("scripts/tocmd", shown.stdout)

    def tmp(self):
        return Path(self.enterContext(self.temporary_dir()))

    def temporary_dir(self):
        import tempfile

        return tempfile.TemporaryDirectory()


def write(directory, name, text):
    path = directory / name
    path.write_text(text)
    return path


if __name__ == "__main__":
    unittest.main()
