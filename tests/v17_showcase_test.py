"""outer.v17.M5 — EXPLANATION.md showcase after Steckbrief."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "presentation-bridge"
TEMPLATE = ROOT / "presentation" / "bridge" / "steckbrief.md"
EXPLANATION = ROOT / "workshop" / "results" / "refine-1" / "EXPLANATION.md"
REFINE1 = ROOT / "presentation" / "lessons" / "lesson-refine1.md"
BUILD_DECK = ROOT / "presentation" / ".bin" / "build-deck"


class ShowcaseM5(unittest.TestCase):
    def test_refine1_explanation_layout_exists(self):
        self.assertTrue(EXPLANATION.is_file())
        text = EXPLANATION.read_text(encoding="utf-8")
        self.assertIn("<!-- showcase:begin -->", text)
        self.assertIn("<!-- showcase:end -->", text)
        self.assertNotIn("2026-09-28-22-", text)  # not a dump of every stamp

    def test_live_refine1_appends_showcase_after_steckbrief(self):
        # Ensure bridge has run with current EXPLANATION.
        subprocess.run(
            ["python3", str(BRIDGE), "--overwrite"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        text = REFINE1.read_text(encoding="utf-8")
        steck = text.index("<!-- steckbrief:generated -->")
        show = text.index("<!-- showcase:from")
        self.assertLess(steck, show)
        self.assertNotIn("## Showcase", text)
        self.assertIn("## Results: Run 1 vs Run 2", text)
        self.assertIn("## Results: Run 2 vs Run 3", text)
        self.assertIn("They both differ in lengths and structure.", text)
        self.assertIn("207 lines", text)
        self.assertIn("12126 bytes", text)
        self.assertIn("565 bytes", text)
        self.assertIn(
            "just tocmd workshop/results/refine-1/2026-09-27-22-50-35/docs/specs/SPEC.v1-todo-list-cli-mvp.md",
            text,
        )
        self.assertIn(
            "just tocmd workshop/results/refine-1/2026-09-28-13-02-13/docs/specs/SPEC.v1-todo-list-cli-mvp.md",
            text,
        )
        # Stamps appear only in reproduce paths, not as column labels.
        after = text.split("<!-- showcase:from", 1)[-1]
        self.assertNotIn("Three **PASS** simulates", after)
        self.assertNotRegex(after, r"\*\*Run 1\*\*.*`2026-09-27-22-50-35`")
        self.assertIn("class=\"reproduce\"", after)
        # TOC outlines keep a real H1 inside fences (not demoted by the bridge).
        self.assertIn("# SPEC v1 — Todo List CLI (MVP)", text)
        # Results slides are after the prompt/observations vertical.
        self.assertLess(text.index("*EXPECTED OBSERVATIONS*"), show)
        # One visible title per vertical; fence TOC ## lines do not count.
        gate = subprocess.run(
            [str(ROOT / "scripts" / "slide-double-heading"), str(REFINE1)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(gate.returncode, 0, gate.stderr + gate.stdout)

    def test_fixture_showcase_lands_after_steckbrief_in_assembled_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lessons = root / "lessons"
            lessons.mkdir()
            results = root / "results" / "demo-lesson"
            results.mkdir(parents=True)
            (results / "EXPLANATION.md").write_text(
                textwrap.dedent(
                    """\
                    # Ignore me

                    <!-- showcase:begin -->

                    ## Worth showing

                    - A curated outcome from a prior run.

                    <!-- showcase:end -->
                    """
                ),
                encoding="utf-8",
            )
            journey = root / "JOURNEY.md"
            journey.write_text(
                textwrap.dedent(
                    """\
                    # demo-lesson: Demo title

                    Intro for demo.

                    *WORKTREE*
                    ```
                    .
                    └── README.md
                    ```

                    *PROMPT TO TEST*
                    ```
                    do the thing
                    ```

                    *EXPECTED OBSERVATIONS*
                    - It works.
                    """
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.yaml"
            bindings.write_text(
                "- exercise: journey1\n  lesson: demo-lesson\n  name: Journey\n",
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
                    "--template",
                    str(TEMPLATE),
                    "--results",
                    str(root / "results"),
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(gen.returncode, 0, gen.stderr)
            exercise = (lessons / "journey1.md").read_text(encoding="utf-8")
            self.assertIn("<!-- steckbrief:generated -->", exercise)
            self.assertIn("<!-- showcase:from", exercise)
            self.assertLess(
                exercise.index("<!-- steckbrief:generated -->"),
                exercise.index("<!-- showcase:from"),
            )
            self.assertIn("Worth showing", exercise)
            self.assertNotIn("# Ignore me", exercise)  # demoted / outside region

            fake_pres = root / "presentation"
            fake_pres.mkdir()
            (fake_pres / "lessons").symlink_to(lessons)
            (fake_pres / "assets").mkdir()
            bin_dir = fake_pres / ".bin"
            bin_dir.mkdir()
            patched = BUILD_DECK.read_text(encoding="utf-8").replace(
                "PRES = Path(__file__).resolve().parent.parent",
                f"PRES = Path({str(fake_pres)!r})",
            )
            patched = patched.replace(
                "        run_bridge()\n",
                "        pass  # fixture: lessons already generated\n",
                1,
            )
            patched_path = bin_dir / "build-deck"
            patched_path.write_text(patched, encoding="utf-8")
            patched_path.chmod(0o755)
            (fake_pres / "deck-software-part1.md").write_text(
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
            self.assertLess(
                assembled.index("steckbrief:generated"),
                assembled.index("showcase:from"),
            )
            self.assertIn("Worth showing", assembled)


if __name__ == "__main__":
    unittest.main()
