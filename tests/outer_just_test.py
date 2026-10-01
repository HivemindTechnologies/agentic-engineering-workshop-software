import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INNER = ROOT / "workshop" / "material" / "00-base" / "justfile"


class OuterJustTest(unittest.TestCase):
    def test_outer_test_runs_the_harness_suite_with_host_python(self):
        shown = subprocess.run(["just", "--show", "test"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("python3 -m unittest discover -s tests -p '*_test.py'", shown.stdout)
        inner = INNER.read_text()
        self.assertNotIn("python", inner)
        self.assertIn("sbt test", inner)


if __name__ == "__main__":
    unittest.main()
