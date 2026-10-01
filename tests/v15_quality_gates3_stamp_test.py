"""outer.v15.M1 — quality-gates-3 simulate stamp holds develop_quality-gates-3.v1."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "workshop" / "results" / "quality-gates-3"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"
STATUS = ROOT / "workshop" / "results" / "status.yaml"


def newest_stamp():
    if not RESULTS.is_dir():
        return None
    stamps = sorted(
        p for p in RESULTS.iterdir() if p.is_dir() and len(p.name) == 19 and p.name[4] == "-"
    )
    return stamps[-1] if stamps else None


class QualityGates3Stamp(unittest.TestCase):
    def test_a_stamp_exists_with_tree_and_v1_spec(self):
        self.assertTrue(RESULTS.is_dir(), "workshop/results/quality-gates-3 missing")
        stamp = newest_stamp()
        self.assertIsNotNone(stamp, "no quality-gates-3 result stamp")
        tree = stamp / "TREE"
        self.assertTrue(tree.is_file(), f"missing TREE in {stamp}")
        specs = list((stamp / "docs" / "specs").glob("SPEC.v1*.md"))
        self.assertTrue(specs, f"no develop_quality-gates-3.v1 SPEC.v1*.md under {stamp}/docs/specs")
        # Structure-check shape: at least one milestone heading with Status
        text = specs[0].read_text(encoding="utf-8")
        self.assertIn("(Status:", text)
        self.assertIn("**Acceptance Criteria:**", text)

    def test_journey_or_status_names_the_stamp(self):
        stamp = newest_stamp()
        self.assertIsNotNone(stamp)
        journey = JOURNEY.read_text(encoding="utf-8")
        status = STATUS.read_text(encoding="utf-8") if STATUS.is_file() else ""
        named = stamp.name in journey or stamp.name in status
        self.assertTrue(
            named,
            f"stamp {stamp.name} not referenced in JOURNEY.md or status.yaml",
        )


if __name__ == "__main__":
    unittest.main()
