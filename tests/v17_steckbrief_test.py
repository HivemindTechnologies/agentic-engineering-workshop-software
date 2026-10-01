"""outer.v17.M2b — Steckbrief template, sync, and skill."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "presentation-bridge"
TEMPLATE = ROOT / "presentation" / "bridge" / "steckbrief.md"
SKILL = ROOT / ".claude" / "skills" / "steckbrief" / "SKILL.md"
REFINE1 = ROOT / "presentation" / "lessons" / "lesson-refine1.md"


class SteckbriefM2b(unittest.TestCase):
    def test_template_has_prepare_worktree_column_and_measure_slot(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("{{PREPARE}}", text)
        self.assertIn("{{WORKTREE}}", text)
        self.assertIn("{{PROMPT_AND_OBS}}", text)
        self.assertIn("{{MEASURES}}", text)
        self.assertIn("----", text)
        self.assertIn("<!-- hand:begin -->", text)
        self.assertIn("*PREPARE*", text)
        self.assertIn("*WORKTREE*", text)
        self.assertIn('class="two-column"', text)
        # Prompt/obs labels are emitted by the bridge (combined or split).
        self.assertEqual(text.count("\n----\n"), 2)
        self.assertIn("## {{NAME}} {{NUM}}", text)
        self.assertNotIn("## Prepare", text)
        self.assertNotIn("## Worktree", text)
        self.assertNotIn("## Prompt and observations", text)
        # No accidental editor line-number residue after MEASURES.
        self.assertNotRegex(text, r"\{\{MEASURES\}\}\n\s+\d+\|")

    def test_intro_skips_prepare_fence_when_journey_has_no_prose(self):
        import runpy

        mod = runpy.run_path(str(BRIDGE))
        body = textwrap.dedent(
            """\
            Minimum Runtime: 01:00
            [develop](develop/)

            ```sh
            just prepare refine-2
            just claude
            ```

            *WORKTREE*
            ```
            .
            ```
            """
        )
        intro = mod["intro_paragraph"](body)
        self.assertNotIn("just prepare", intro)
        self.assertNotIn("just claude", intro)
        self.assertEqual(intro, "")

    def test_skill_triggers_on_steckbrief_language(self):
        self.assertTrue(SKILL.is_file())
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Steckbrief", text)
        self.assertIn("journey-slide", text)
        self.assertIn("lesson-backed", text)
        self.assertIn("presentation-bridge", text)
        self.assertIn("--overwrite", text)

    def test_fixture_generation_fills_steckbrief_and_preserves_hand_region(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lessons = root / "lessons"
            lessons.mkdir()
            journey = root / "JOURNEY.md"
            journey.write_text(
                textwrap.dedent(
                    """\
                    # demo-lesson: Demo title (last: PASS 2026-01-01-00-00-00)
                    Minimum Runtime: 01:02
                    Last Token Usage: 12.3k
                    [Results](workshop/results/demo-lesson/2026-01-01-00-00-00)

                    Intro line for the demo.

                    ```sh
                    just prepare demo-lesson
                    just claude
                    ```

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
                    - It does the thing.
                    """
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.yaml"
            bindings.write_text(
                "- exercise: journey1\n  lesson: demo-lesson\n  name: Journey\n",
                encoding="utf-8",
            )
            template = TEMPLATE.read_text(encoding="utf-8")

            first = subprocess.run(
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
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            path = lessons / "journey1.md"
            body = path.read_text(encoding="utf-8")
            self.assertTrue(body.startswith("# 🏝️ Journey 1"))
            self.assertIn("<!-- steckbrief:generated -->", body)
            self.assertIn("Minimum Runtime: 01:02", body)
            self.assertIn("just prepare demo-lesson", body)
            self.assertIn("README.md", body)
            self.assertIn("do the thing", body)
            self.assertIn("It does the thing.", body)
            self.assertIn("*PREPARE*", body)
            self.assertIn("*WORKTREE*", body)
            self.assertIn("*PROMPT TO TEST*", body)
            self.assertIn('class="two-column"', body)
            # Title h1 + combined prepare/worktree + prompt/obs (≥2 h2s).
            self.assertGreaterEqual(body.count("\n## Journey 1\n"), 2)

            # Hand tweak survives a second sync.
            path.write_text(HAND_SWAP(body), encoding="utf-8")

            second = subprocess.run(
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
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            again = path.read_text(encoding="utf-8")
            self.assertIn("Hand kept for facilitators", again)
            self.assertIn("do the thing", again)

            wiped = subprocess.run(
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
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(wiped.returncode, 0, wiped.stderr)
            self.assertNotIn(
                "Hand kept for facilitators", path.read_text(encoding="utf-8")
            )

    def test_live_refine1_steckbrief_matches_template_shape(self):
        self.assertTrue(REFINE1.is_file())
        text = REFINE1.read_text(encoding="utf-8")
        self.assertIn("<!-- steckbrief:generated -->", text)
        self.assertIn("<!-- backing-lesson: refine-1 -->", text)
        self.assertIn("**First non standard refine prompt.**", text)
        self.assertNotIn("**Sandbox lesson", text)
        self.assertIn("*PREPARE*", text)
        self.assertIn("*WORKTREE*", text)
        self.assertIn("*PROMPT TO TEST*", text)
        self.assertIn("Minimum Runtime", text)
        self.assertIn('class="two-column"', text)
        # Prepare+worktree share one vertical; prompt/obs is another (≥2 h2s).
        self.assertGreaterEqual(text.count("\n## Refine 1\n"), 2)
        # PREPARE and WORKTREE must not be separate verticals anymore.
        prepare_at = text.index("*PREPARE*")
        worktree_at = text.index("*WORKTREE*")
        between = text[prepare_at:worktree_at]
        self.assertNotIn("\n----\n", between)
        self.assertNotIn("\n## Prepare\n", text)
        self.assertNotIn("\n## Worktree\n", text)
        self.assertNotIn("\n## Prompt and observations\n", text)
        # Paths readable without hover.
        self.assertIn("Results: `workshop/results/refine-1/", text)
        self.assertNotIn("[Results](", text)
        # The deck carries no speaker notes.
        self.assertNotIn("Note:", text)
        # Prompt fence is soft-wrapped to multiple lines.
        prompt_block = text.split("*PROMPT TO TEST*", 1)[1].split("*EXPECTED", 1)[0]
        fence = prompt_block.split("```", 2)[1].strip("\n")
        self.assertGreater(fence.count("\n"), 0)
        # Short refine-1 prompt stays on one slide with observations.
        self.assertIn('class="steckbrief-prompt-obs"', text)
        self.assertNotIn('class="steckbrief-prompt"', text)
        self.assertNotIn('class="steckbrief-obs"', text)

    def test_long_prompt_splits_observations_onto_next_vertical(self):
        import runpy

        mod = runpy.run_path(str(BRIDGE))
        short_prompt = "```plaintext\none line\n```"
        short_obs = "- a\n- b"
        combined = mod["render_prompt_and_obs"]("Refine", "1", short_prompt, short_obs)
        self.assertIn("steckbrief-prompt-obs", combined)
        self.assertIn("*PROMPT TO TEST*", combined)
        self.assertIn("*EXPECTED OBSERVATIONS*", combined)
        self.assertNotIn("\n----\n", combined)

        long_lines = "\n".join(f"line {i} " + ("word " * 10) for i in range(12))
        long_prompt = (
            f"```plaintext\n{mod['wrap_prompt_text'](long_lines)}\n```"
        )
        split = mod["render_prompt_and_obs"]("Refine", "4", long_prompt, short_obs)
        self.assertIn("steckbrief-prompt", split)
        self.assertIn("steckbrief-obs", split)
        self.assertIn("\n----\n", split)
        self.assertLess(split.index("*PROMPT TO TEST*"), split.index("\n----\n"))
        self.assertLess(split.index("\n----\n"), split.index("*EXPECTED OBSERVATIONS*"))


def HAND_SWAP(body: str) -> str:
    return body.replace(
        "<!-- hand:begin -->",
        "<!-- hand:begin -->\nHand kept for facilitators",
        1,
    )


if __name__ == "__main__":
    unittest.main()
