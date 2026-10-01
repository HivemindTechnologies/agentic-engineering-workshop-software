"""The judge recipe must survive nono's log noise and must show the lesson's expected files."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JUSTFILE = (ROOT / "justfile").read_text(encoding="utf-8")
FILTER = (
    "[inputs | fromjson? | select(type==\"object\" and .type==\"result\" and .subtype==\"success\")]"
    " | last | .result // empty"
)


class JudgeRecipe(unittest.TestCase):
    def test_no_result_extraction_uses_the_intolerant_slurp(self):
        self.assertNotIn("jq -rs 'map(select(.type==\"result\"", JUSTFILE)
        self.assertEqual(JUSTFILE.count("fromjson?"), 3)

    def test_the_filter_reads_past_a_coloured_warning_line(self):
        if shutil.which("jq") is None:
            self.skipTest("jq not on PATH")
        log = Path(tempfile.mkdtemp()) / "log"
        log.write_text(
            "\x1b[2m2026 \x1b[33m WARN\x1b[0m Before-hook failed\n"
            '{"type":"result","subtype":"success","result":"verdict: pass"}\n'
        )
        out = subprocess.run(["jq", "-Rrn", FILTER, str(log)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "verdict: pass")

    def test_specs_are_the_expected_markdown_not_every_markdown_file(self):
        self.assertNotIn("find \"$results/$s\" -name '*.md'", JUSTFILE)
        self.assertIn("lesson-forks\" paths \"$lesson\"", JUSTFILE)

    def test_expected_non_markdown_files_are_shown_to_the_judge(self):
        self.assertIn("extra_files()", JUSTFILE)
        self.assertIn('extra_files "$results/$s"', JUSTFILE)


if __name__ == "__main__":
    unittest.main()
