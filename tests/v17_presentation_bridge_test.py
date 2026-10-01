"""outer.v17.M2a — bridge journey lessons into deck exercises."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "presentation-bridge"
BUILD_DECK = ROOT / "presentation" / ".bin" / "build-deck"
README = ROOT / "presentation" / "bridge" / "README.md"
JUST = ROOT / "justfile"


class PresentationBridgeM2a(unittest.TestCase):
    def test_bridge_docs_describe_exercise_not_second_slide_kind(self):
        text = README.read_text(encoding="utf-8").lower()
        self.assertIn("every unit in the reveal-md deck is an **exercise**".replace("**", ""), text.replace("**", ""))
        self.assertIn("lesson-backed", text)
        self.assertIn("not a second slide kind", text)

    def test_just_present_has_no_separate_bridge_recipe(self):
        just = JUST.read_text(encoding="utf-8")
        self.assertNotRegex(just, r"(?m)^present-bridge\b")
        self.assertRegex(just, r"(?m)^present\b")
        self.assertRegex(just, r"(?m)^present-build\b")
        build_deck = (ROOT / "presentation" / ".bin" / "build-deck").read_text(
            encoding="utf-8"
        )
        self.assertIn("presentation-bridge", build_deck)
        self.assertIn("run_bridge", build_deck)
        shown = subprocess.run(
            ["just", "--show", "present"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn(".bin/present", shown.stdout)
        self.assertIn("rebuild", shown.stdout)
        self.assertIn("PRESENT_REBUILD", shown.stdout)

    def test_fixture_spine_splices_backing_lesson_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lessons = root / "lessons"
            lessons.mkdir()
            journey = root / "JOURNEY.md"
            journey.write_text(
                textwrap.dedent(
                    """\
                    # demo-lesson: Demo title here

                    Intro paragraph for the demo lesson that should appear on the card.

                    *PROMPT TO TEST*
                    ```
                    hello
                    ```
                    """
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.yaml"
            bindings.write_text(
                "- exercise: journey1\n  lesson: demo-lesson\n  name: Journey\n",
                encoding="utf-8",
            )
            # Minimal assets so assemble can symlink assets/
            (root / "assets").mkdir()
            spine = root / "deck-software-part1.md"
            spine.write_text(
                textwrap.dedent(
                    """\
                    ---
                    title: Fixture
                    ---

                    <h1 class="title">Fixture Deck</h1>

                    <!-- lessons:
                    == Part 1
                    -- Bridge demo
                    journey1
                    -->

                    ---

                    ## Done
                    """
                ),
                encoding="utf-8",
            )

            gen = subprocess.run(
                [
                    "python3",
                    str(BRIDGE),
                    "--bindings",
                    str(bindings),
                    "--journey",
                    str(journey),
                    "--lessons-dir",
                    str(lessons),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(gen.returncode, 0, gen.stderr)
            exercise = (lessons / "journey1.md").read_text(encoding="utf-8")
            self.assertIn("<!-- backing-lesson: demo-lesson -->", exercise)
            self.assertIn("demo-lesson", exercise)
            self.assertTrue(exercise.startswith("# 🏝️ Journey 1"))

            # Point build-deck at this fixture tree by running from a copied layout.
            # build-deck resolves PRES relative to .bin; invoke via env override by
            # writing a tiny runner that temporarily is not needed — instead call
            # assemble logic through a subprocess with cwd trick: copy .bin/build-deck
            # is fixed to presentation/. So we patch by placing files under a fake
            # presentation root and invoking python with modified path... Easiest:
            # run build-deck's assemble by importing after chdir isn't possible.
            # Use subprocess to run a one-liner that duplicates PRES layout.
            fake_pres = root / "presentation"
            fake_pres.mkdir()
            (fake_pres / "lessons").symlink_to(lessons)
            (fake_pres / "assets").mkdir()
            bin_dir = fake_pres / ".bin"
            bin_dir.mkdir()
            build_src = BUILD_DECK.read_text(encoding="utf-8")
            # Rewrite PRES to fake_pres absolute path for this run.
            patched = build_src.replace(
                "PRES = Path(__file__).resolve().parent.parent",
                f"PRES = Path({str(fake_pres)!r})",
            )
            patched_path = bin_dir / "build-deck"
            patched_path.write_text(patched, encoding="utf-8")
            patched_path.chmod(0o755)
            (fake_pres / "deck-software-part1.md").write_text(
                spine.read_text(encoding="utf-8"), encoding="utf-8"
            )

            built = subprocess.run(
                ["python3", str(patched_path), "deck-software-part1.md"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(built.returncode, 0, built.stderr + built.stdout)
            assembled = (fake_pres / ".build" / "deck-software-part1.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("backing-lesson: demo-lesson", assembled)
            self.assertIn("Journey 1", assembled)


if __name__ == "__main__":
    unittest.main()
