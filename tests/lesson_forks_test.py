import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORKS = ROOT / "scripts" / "lesson-forks"
STATUS = ROOT / "scripts" / "lesson-status"
JUSTFILE = ROOT / "justfile"

PRESENCE = textwrap.dedent(
    """\
    import os, sys
    from pathlib import Path
    marker = Path("docs/specs/out.md")
    order = Path(os.environ["ORDER"])
    with order.open("a") as handle:
        handle.write("start\\n")
    existed = "present" if marker.exists() else "absent"
    with Path(os.environ["SEEN"]).open("a") as handle:
        handle.write(existed + "\\n")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("written\\n")
    with order.open("a") as handle:
        handle.write("end\\n")
    sys.stdout.write('{"type": "result", "num_turns": 1}\\n')
    sys.stdout.flush()
    sys.stdin.read()
    """
)

DEPTH = textwrap.dedent(
    """\
    import json, sys
    seen = 0
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        seen += 1
        sys.stdout.write(json.dumps({"type": "result", "num_turns": seen}) + "\\n")
        sys.stdout.flush()
    """
)

def git(work, *args, env=None):
    subprocess.run(["git", "-C", str(work), *args], check=True, env=env, capture_output=True, text=True)


class LessonForks(unittest.TestCase):
    def test_depth_caps_each_fork_and_default_is_one_fork(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        results = Path(self.enterContext(tempfile.TemporaryDirectory()))
        fake = Path(self.enterContext(tempfile.TemporaryDirectory())) / "depth.py"
        fake.write_text(DEPTH)
        one = self.run_forks(work, results, fake, forks=None, depth=None, stamps=["2026-09-28-13-10-01"])
        self.assertEqual(one.returncode, 0, one.stderr)
        self.assertEqual(len(list(results.iterdir())), 1)

        results2 = Path(self.enterContext(tempfile.TemporaryDirectory()))
        proc = self.run_forks(
            work,
            results2,
            fake,
            forks=2,
            depth=3,
            stamps=["2026-09-28-13-10-02", "2026-09-28-13-10-03"],
            prepared=self.commit(work),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for stamp in ("2026-09-28-13-10-02", "2026-09-28-13-10-03"):
            measures = subprocess.run(
                [str(STATUS), "measures", str(results2 / stamp / "session.jsonl")],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertRegex(
                measures.stdout,
                r"^interactions=3 length=absent wall_seconds=[1-9][0-9]* capped=yes\n$",
            )

    def test_second_fork_starts_from_the_prepared_tree_after_the_first_finishes(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        results = Path(self.enterContext(tempfile.TemporaryDirectory()))
        outside = Path(self.enterContext(tempfile.TemporaryDirectory()))
        seen = outside / "seen"
        order = outside / "order"
        fake = outside / "presence.py"
        fake.write_text(PRESENCE)
        sha = self.commit(work)
        env = os.environ.copy()
        env["SEEN"] = str(seen)
        env["ORDER"] = str(order)
        proc = self.run_forks(
            work,
            results,
            fake,
            forks=2,
            depth=None,
            stamps=["2026-09-28-13-11-01", "2026-09-28-13-11-02"],
            prepared=sha,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(seen.read_text(), "absent\nabsent\n")
        self.assertEqual(order.read_text(), "start\nend\nstart\nend\n")
        self.assertTrue((results / "2026-09-28-13-11-01" / "session.jsonl").is_file())
        self.assertTrue((results / "2026-09-28-13-11-02" / "session.jsonl").is_file())

    def test_same_stamp_fails_before_the_second_write(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        results = Path(self.enterContext(tempfile.TemporaryDirectory()))
        collided = results / "2026-09-28-13-12-02"
        collided.mkdir()
        (collided / "session.jsonl").write_text("keep\n")
        fake = Path(self.enterContext(tempfile.TemporaryDirectory())) / "depth.py"
        fake.write_text(DEPTH)
        proc = self.run_forks(
            work,
            results,
            fake,
            forks=2,
            depth=None,
            stamps=["2026-09-28-13-12-01", "2026-09-28-13-12-02"],
            prepared=self.commit(work),
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("stamp exists:", proc.stderr)
        self.assertEqual((collided / "session.jsonl").read_text(), "keep\n")
        self.assertTrue((results / "2026-09-28-13-12-01" / "session.jsonl").is_file())

    def test_judge_minimum_follows_the_fork_count(self):
        one = subprocess.run([str(FORKS), "judge-min", "1"], capture_output=True, text=True, check=True)
        two = subprocess.run([str(FORKS), "judge-min", "2"], capture_output=True, text=True, check=True)
        self.assertEqual(one.stdout, "1\n")
        self.assertEqual(two.stdout, "2\n")

    def test_status_line_uses_the_newest_session(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / "JOURNEY.md").write_text("# refine-1: First\n")
        older = root / "refine-1" / "2026-09-28-13-13-01"
        newer = root / "refine-1" / "2026-09-28-13-13-02"
        older.mkdir(parents=True)
        newer.mkdir(parents=True)
        (older / "session.jsonl").write_text('{"type": "result", "num_turns": 1}\n')
        (newer / "session.jsonl").write_text('{"type": "result", "num_turns": 9}\n')
        proc = subprocess.run([str(STATUS), "lines", str(root), "refine-1"], capture_output=True, text=True)
        self.assertIn("interactions=9", proc.stdout)
        self.assertNotIn("interactions=1", proc.stdout)
        self.assertNotIn("forks=", proc.stdout)

    def test_simulate_rejects_max_and_forks_before_claude(self):
        denied = subprocess.run(["just", "simulate", "refine-1", "max=2"], capture_output=True, text=True)
        self.assertEqual(denied.returncode, 1)
        self.assertIn("use depth=", denied.stderr)
        self.assertNotIn("simulation", denied.stdout)
        forks = subprocess.run(["just", "simulate", "refine-1", "forks=2"], capture_output=True, text=True)
        self.assertEqual(forks.returncode, 1)
        self.assertIn("forks is a parameter of just validate", forks.stderr)
        self.assertNotIn("simulation", forks.stdout)

    def test_every_lesson_through_implement_1_has_an_expected_path(self):
        lessons = (
            "refine-1",
            "refine-1a",
            "refine-2",
            "refine-3",
            "refine-4",
            "refine-5",
            "refine-6",
            "implement-1",
        )
        forks = ROOT / "scripts" / "lesson-forks"
        for lesson in lessons:
            result = subprocess.run([str(forks), "paths", lesson], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("docs/specs/SPEC.v1-todo-list-cli-mvp.md", result.stdout)
        implement = subprocess.run([str(forks), "paths", "implement-1"], capture_output=True, text=True)
        self.assertIn("build.sbt", implement.stdout)
        justfile = JUSTFILE.read_text()
        self.assertIn("scripts/lesson-order", justfile)
        renamed = subprocess.run(["just", "validate", "refine-3", "max=2"], capture_output=True, text=True)
        self.assertEqual(renamed.returncode, 1)
        self.assertIn("use depth=", renamed.stderr)

    def test_the_overlap_spike_is_not_in_the_harness(self):
        self.assertNotIn("prove-parallel", JUSTFILE.read_text())
        self.assertFalse((ROOT / "scripts" / "prove-parallel").exists())

    def commit(self, work):
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "test"
        env["GIT_AUTHOR_EMAIL"] = "test@example.com"
        env["GIT_COMMITTER_NAME"] = "test"
        env["GIT_COMMITTER_EMAIL"] = "test@example.com"
        git(work, "init", "-b", "main")
        (work / "README").write_text("base\n")
        git(work, "add", "README", env=env)
        git(work, "commit", "-m", "base", env=env)
        sha = subprocess.run(["git", "-C", str(work), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return sha.stdout.strip()

    def run_forks(self, work, results, fake, forks, depth, stamps, prepared="", env=None):
        args = [str(FORKS), "run", "--work", str(work), "--results", str(results), "--message", "lesson"]
        if forks is not None:
            args += ["--forks", str(forks)]
        if depth is not None:
            args += ["--depth", str(depth)]
        if prepared:
            args += ["--prepared", prepared]
        for stamp in stamps:
            args += ["--stamp", stamp]
        args += ["--expect", "docs/specs/out.md", "--", "python3", str(fake)]
        return subprocess.run(args, capture_output=True, text=True, env=env)


if __name__ == "__main__":
    unittest.main()
