"""outer.v17.M1 — software presentation port into this repo."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "presentation"
DOCS_DRAWINGS = ROOT / "docs" / "drawings"
JUST = ROOT / "justfile"

# One distinctive file from the source presentation drawings merge.
SOURCE_DRAWING = "quality-gates.excalidraw"
# Pre-existing outer drawing that must survive the merge.
OUTER_DRAWING = "sprouts.excalidraw"


class PresentationPortM1(unittest.TestCase):
    def test_software_presentation_tree_exists_without_infra_spine(self):
        for relative in (
            "deck-software-part1.md",
            "package.json",
            "package-lock.json",
            "reveal.json5",
            "theme/hivemind.css",
            "theme/hivemind.js",
            "assets/fonts",
            "assets/images",
            "lessons/_template.md",
            ".bin/present",
            ".bin/build-deck",
            ".bin/check",
            ".bin/stop",
        ):
            path = PRESENTATION / relative
            self.assertTrue(path.exists(), f"missing {relative}")
        self.assertFalse((PRESENTATION / "deck-infrastructure.md").exists())
        self.assertFalse((PRESENTATION / "deck-software-part2.md").exists())
        self.assertTrue((PRESENTATION / ".bin" / "present").stat().st_mode & 0o111)

    def test_drawings_merged_into_docs_without_losing_sprouts(self):
        self.assertTrue((DOCS_DRAWINGS / OUTER_DRAWING).is_file())
        self.assertTrue((DOCS_DRAWINGS / SOURCE_DRAWING).is_file())
        # Source drawings are reachable from the presentation tree (symlink or copy).
        drawn = PRESENTATION / "drawings"
        self.assertTrue(drawn.exists())
        self.assertTrue((drawn / SOURCE_DRAWING).exists())

    def test_just_present_recipes_wrap_presentation_commands(self):
        just = JUST.read_text(encoding="utf-8")
        for recipe in ("present", "present-build", "present-stop", "present-check"):
            self.assertRegex(just, rf"(?m)^{recipe}(\s|$|:)", msg=recipe)
            shown = subprocess.run(
                ["just", "--show", recipe],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(shown.returncode, 0, f"{recipe}: {shown.stderr}")
            self.assertIn("presentation", shown.stdout)

        present = subprocess.run(
            ["just", "--show", "present"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(present.returncode, 0, present.stderr)
        # Default deck is software Part 1; rebuild=yes folds build into present.
        self.assertRegex(present.stdout, r"software-part1|\.bin/present")
        self.assertIn('rebuild="yes"', present.stdout.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
