"""slide-double-heading — at most one #/## title per reveal slide."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "slide-double-heading"
LESSONS = ROOT / "presentation" / "lessons"


class SlideDoubleHeading(unittest.TestCase):
    def test_live_lessons_pass(self):
        result = subprocess.run(
            [str(SCRIPT), str(LESSONS)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("ok", result.stdout)

    def test_fixture_double_title_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.md"
            path.write_text(
                textwrap.dedent(
                    """\
                    ## Showcase

                    ## Run 1 vs Run 2

                    body

                    ```plaintext
                    # SPEC inside fence is fine
                    ## also fine
                    ```
                    """
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [str(SCRIPT), str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FAILED", result.stderr)
            self.assertIn("## Showcase", result.stderr)
            self.assertIn("## Run 1 vs Run 2", result.stderr)

    def test_headings_inside_fences_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.md"
            path.write_text(
                textwrap.dedent(
                    """\
                    ## Results: Run 1 vs Run 2

                    ```plaintext
                    # SPEC v1
                    ## Summary
                    ## Goals
                    ```
                    """
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [str(SCRIPT), str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
