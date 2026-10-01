import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "scripts" / "capture-result-tree"
RESTORE = ROOT / "scripts" / "restore-result"
PRUNED = ROOT / "scripts" / "pruned-tree"
OBS = ROOT / "scripts" / "observation-distance"
JUSTFILE = ROOT / "justfile"


class CaptureResultTree(unittest.TestCase):
    def test_copies_files_outside_the_expected_path_list(self):
        tmp = Path(tempfile.mkdtemp())
        work = tmp / "develop"
        stamp = tmp / "stamp"
        (work / "docs" / "specs").mkdir(parents=True)
        (work / "docs" / "specs" / "SPEC.md").write_text("spec\n")
        (work / "justfile").write_text("check:\n")
        (work / "src" / "main").mkdir(parents=True)
        (work / "src" / "main" / "App.scala").write_text("object App\n")
        (work / "target" / "noise").mkdir(parents=True)
        (work / "target" / "noise" / "x.class").write_text("x")
        (work / ".git").mkdir()
        (work / ".git" / "HEAD").write_text("ref\n")
        stamp.mkdir()
        (stamp / "session.jsonl").write_text("{}\n")
        result = subprocess.run(
            ["bash", str(CAPTURE), str(work), str(stamp)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((stamp / "justfile").is_file())
        self.assertTrue((stamp / "src" / "main" / "App.scala").is_file())
        self.assertTrue((stamp / "docs" / "specs" / "SPEC.md").is_file())
        self.assertTrue((stamp / "session.jsonl").is_file())
        self.assertFalse((stamp / "target").exists())
        self.assertFalse((stamp / ".git").exists())

    def test_simulate_recipe_calls_capture_result_tree(self):
        text = JUSTFILE.read_text()
        self.assertIn("scripts/capture-result-tree", text)


class RestoreResult(unittest.TestCase):
    def test_restore_newest_stamp_into_work_and_writes_record(self):
        tmp = Path(tempfile.mkdtemp())
        results = tmp / "results" / "refine-1"
        older = results / "2026-09-28-01-00-00"
        newer = results / "2026-09-28-02-00-00"
        for stamp, body in ((older, "old\n"), (newer, "new\n")):
            stamp.mkdir(parents=True)
            (stamp / "justfile").write_text(body)
            (stamp / "session.jsonl").write_text("{}\n")
        work = tmp / "develop"
        record = tmp / "prepare-lesson"
        result = subprocess.run(
            ["bash", str(RESTORE), str(results), str(work), str(record)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((work / "justfile").read_text(), "new\n")
        self.assertFalse((work / "session.jsonl").exists())
        self.assertEqual(record.read_text(), "refine-1\n")

    def test_restore_named_stamp(self):
        tmp = Path(tempfile.mkdtemp())
        results = tmp / "results" / "refine-1"
        stamp = results / "2026-09-28-01-00-00"
        stamp.mkdir(parents=True)
        (stamp / "note").write_text("keep\n")
        work = tmp / "develop"
        record = tmp / "prepare-lesson"
        result = subprocess.run(
            ["bash", str(RESTORE), str(results), str(work), str(record), "2026-09-28-01-00-00"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((work / "note").read_text(), "keep\n")


class ObservationDistance(unittest.TestCase):
    def test_check_baseline_fails_when_observation_drifts(self):
        tmp = Path(tempfile.mkdtemp())
        journey = tmp / "JOURNEY.md"
        journey.write_text(
            "\n".join(
                [
                    "# a: One",
                    "*EXPECTED OBSERVATIONS*",
                    "- alpha one shared",
                    "",
                    "# b: Two",
                    "*EXPECTED OBSERVATIONS*",
                    "- alpha one shared still",
                    "",
                    "# c: Three",
                    "*EXPECTED OBSERVATIONS*",
                    "- totally different omega zeta",
                    "",
                ]
            )
        )
        board = subprocess.run(
            ["python3", str(OBS), str(journey)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(board.returncode, 0, board.stderr)
        baseline = tmp / "baseline.txt"
        baseline.write_text(board.stdout)
        # edit c so next/previous for b or c moves
        journey.write_text(
            "\n".join(
                [
                    "# a: One",
                    "*EXPECTED OBSERVATIONS*",
                    "- alpha one shared",
                    "",
                    "# b: Two",
                    "*EXPECTED OBSERVATIONS*",
                    "- alpha one shared still",
                    "",
                    "# c: Three",
                    "*EXPECTED OBSERVATIONS*",
                    "- alpha one shared still and more of the same words for drift",
                    "",
                ]
            )
        )
        check = subprocess.run(
            ["python3", str(OBS), str(journey), "--check-baseline", str(baseline), "--threshold", "0.01"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(check.returncode, 0)
        self.assertTrue("b " in check.stdout or "c " in check.stdout, check.stdout)


class JudgeAgentTools(unittest.TestCase):
    def test_judge_recipe_enables_tools_and_allows_results(self):
        text = JUSTFILE.read_text()
        start = text.index("judge lesson")
        end = text.index("\n# One line per lesson", start)
        block = text[start:end]
        self.assertNotIn("--tools", block)
        self.assertIn("--allow \"$results\"", block)
        self.assertIn("--permission-mode acceptEdits", block)


class PrunedTree(unittest.TestCase):
    def _fake_sandbox(self, root: Path) -> None:
        (root / "docs" / "specs").mkdir(parents=True)
        (root / "docs" / "specs" / "SPEC.md").write_text("spec\n")
        (root / "justfile").write_text("check:\n")
        (root / "src" / "main").mkdir(parents=True)
        (root / "src" / "main" / "App.scala").write_text("object App\n")
        (root / "target" / "noise").mkdir(parents=True)
        (root / "target" / "noise" / "junk.class").write_text("x")
        (root / "project" / "target" / "config-classes").mkdir(parents=True)
        (root / "project" / "target" / "config-classes" / "x.class").write_text("x")
        (root / "project" / "build.properties").write_text("sbt.version=1.10.0\n")
        (root / ".git").mkdir()
        (root / ".git" / "HEAD").write_text("ref\n")
        (root / ".claude-home").mkdir()
        (root / ".claude-home" / "secret").write_text("no\n")

    def test_print_skips_target_and_shows_source(self):
        tmp = Path(tempfile.mkdtemp())
        work = tmp / "develop"
        work.mkdir()
        self._fake_sandbox(work)
        result = subprocess.run(
            ["python3", str(PRUNED), str(work)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("justfile", out)
        self.assertIn("App.scala", out)
        self.assertIn("SPEC.md", out)
        self.assertIn("build.properties", out)
        self.assertNotIn("junk.class", out)
        self.assertNotIn("noise", out)
        self.assertNotIn("secret", out)
        self.assertNotIn("HEAD", out)
        # directory names may appear as prune markers or not at all; contents must not
        self.assertNotRegex(out, r"target/.+")

    def test_capture_writes_TREE_without_target_junk(self):
        tmp = Path(tempfile.mkdtemp())
        work = tmp / "develop"
        stamp = tmp / "stamp"
        work.mkdir()
        self._fake_sandbox(work)
        stamp.mkdir()
        (stamp / "session.jsonl").write_text("{}\n")
        result = subprocess.run(
            ["bash", str(CAPTURE), str(work), str(stamp)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        tree_file = stamp / "TREE"
        self.assertTrue(tree_file.is_file(), "capture must write TREE")
        body = tree_file.read_text(encoding="utf-8")
        self.assertIn("App.scala", body)
        self.assertIn("justfile", body)
        self.assertNotIn("junk.class", body)
        self.assertNotIn("secret", body)

    def test_lesson_stamp_newest_and_named(self):
        tmp = Path(tempfile.mkdtemp())
        results = tmp / "results" / "refine-1"
        older = results / "2026-09-28-01-00-00"
        newer = results / "2026-09-28-02-00-00"
        for stamp, name in ((older, "old.txt"), (newer, "new.txt")):
            stamp.mkdir(parents=True)
            (stamp / name).write_text("x\n")
            (stamp / "target" / "nope").mkdir(parents=True)
            (stamp / "target" / "nope" / "x.class").write_text("x")
        newest = subprocess.run(
            ["python3", str(PRUNED), "--results", str(results)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(newest.returncode, 0, newest.stderr)
        self.assertIn("new.txt", newest.stdout)
        self.assertNotIn("old.txt", newest.stdout)
        self.assertNotIn("x.class", newest.stdout)
        named = subprocess.run(
            ["python3", str(PRUNED), "--results", str(results), "--stamp", "2026-09-28-01-00-00"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(named.returncode, 0, named.stderr)
        self.assertIn("old.txt", named.stdout)
        missing = subprocess.run(
            ["python3", str(PRUNED), "--results", str(tmp / "results" / "missing")],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(missing.returncode, 0)

    def test_justfile_exposes_tree_recipe(self):
        text = JUSTFILE.read_text()
        self.assertRegex(text, r"(?m)^tree")
        self.assertIn("scripts/pruned-tree", text)


if __name__ == "__main__":
    unittest.main()
