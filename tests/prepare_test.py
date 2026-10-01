import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PrepareKeep(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.work = self.tmp / "develop"
        self.record = self.tmp / "prepared-lesson"
        self.real_develop = ROOT / "develop"
        self.real_record = ROOT / ".prepare-lesson"
        self.develop_before = self.names(self.real_develop)
        self.record_before = self.real_record.read_bytes() if self.real_record.exists() else None
        self.real_git = shutil.which("git")
        self.git_log = self.tmp / "git.log"
        bindir = self.tmp / "bin"
        bindir.mkdir()
        wrapper = bindir / "git"
        wrapper.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$*\" >> {self.git_log}\n"
            f"exec {self.real_git} \"$@\"\n"
        )
        wrapper.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = str(bindir) + os.pathsep + self.env.get("PATH", "")
        self.env["PREPARE_WORK"] = str(self.work)
        self.env["PREPARE_RECORD"] = str(self.record)
        self.env["GIT_AUTHOR_NAME"] = "Prepare"
        self.env["GIT_AUTHOR_EMAIL"] = "prepare@example.com"
        self.env["GIT_COMMITTER_NAME"] = "Prepare"
        self.env["GIT_COMMITTER_EMAIL"] = "prepare@example.com"
        self.addCleanup(self.assert_this_clone_untouched)

    def test_prepare_without_a_lesson_prints_names_and_writes_nothing(self):
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "refine-1")
        self.assertIn("quality-gates-2\n", result.stdout)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.work.exists())

    def test_unknown_keep_value_does_not_rebuild(self):
        self.work.mkdir()
        (self.work / "planted").write_text("stay")
        before = self.tree()
        result = self.prepare("refine-1", "keep=no")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown prepare flag: keep=no", result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertFalse(self.record.exists())

    def test_full_prepare_rebuilds_records_the_lesson_and_prints_it(self):
        self.work.mkdir()
        (self.work / "planted").write_text("gone")
        home = self.work / ".claude-home"
        home.mkdir()
        (home / "session").write_text("gone")
        result = self.prepare("refine-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.work / "planted").exists())
        self.assertFalse(home.exists())
        self.assertTrue((self.work / "README.md").is_file())
        self.assertEqual(self.commits(), ["base"])
        self.assertIn("init", self.git_subcommands())
        self.assertEqual(self.record.read_text(), "refine-1\n")
        self.assertFalse(any(path.name == ".prepare-lesson" for path in self.work.rglob("*")))
        self.assertIn("# refine-1:", result.stdout)

    def test_keep_applies_deltas_after_the_record_and_leaves_claude_home(self):
        self.prepare("refine-1")
        home = self.work / ".claude-home"
        home.mkdir()
        (home / "session").write_text("stay")
        (self.work / "planted").write_text("stay")
        root = self.head()
        self.git_log.write_text("")
        result = self.prepare("refine-4", "keep=yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((home / "session").read_text(), "stay")
        self.assertEqual((self.work / "planted").read_text(), "stay")
        self.assertTrue((self.work / ".claude/commands/refine.md").is_file())
        self.assertTrue((self.work / "docs/rules/WOW.md").is_file())
        self.assertEqual(self.commits(), ["refine-4", "refine-1a", "base"])
        self.assertEqual(self.root_commit(), root)
        self.assertNotIn("init", self.git_subcommands())
        self.assertEqual(self.record.read_text(), "refine-4\n")
        self.assertIn("# refine-4:", result.stdout)

    def test_empty_delta_advances_the_record_without_a_commit(self):
        self.prepare("refine-2")
        before = self.tree()
        head = self.head()
        result = self.prepare("refine-3", "keep=yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.record.read_text(), "refine-3\n")
        self.assertEqual(self.head(), head)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.commits(), ["refine-1a", "base"])

    def test_keep_rejects_a_missing_record_and_leaves_develop_unchanged(self):
        self.work.mkdir()
        (self.work / "planted").write_text("stay")
        before = self.tree()
        result = self.prepare("refine-2", "keep=yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no recorded lesson", result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertFalse(self.record.exists())

    def test_keep_rejects_an_unknown_recorded_lesson_and_leaves_develop_unchanged(self):
        self.work.mkdir()
        (self.work / "planted").write_text("stay")
        self.record.write_text("not-a-lesson\n")
        before = self.tree()
        result = self.prepare("refine-2", "keep=yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("recorded lesson is unknown: not-a-lesson", result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.record.read_text(), "not-a-lesson\n")

    def test_keep_rejects_a_lesson_before_the_recorded_one(self):
        self.work.mkdir()
        (self.work / "planted").write_text("stay")
        self.record.write_text("refine-4\n")
        before = self.tree()
        result = self.prepare("refine-1", "keep=yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refine-1 is before the recorded lesson refine-4", result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.record.read_text(), "refine-4\n")

    def test_keep_rejects_an_unknown_lesson_and_leaves_develop_unchanged(self):
        self.work.mkdir()
        (self.work / "planted").write_text("stay")
        self.record.write_text("refine-1\n")
        before = self.tree()
        result = self.prepare("nope", "keep=yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown lesson: nope", result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.record.read_text(), "refine-1\n")

    def test_keep_of_the_recorded_lesson_changes_nothing(self):
        self.prepare("refine-1")
        (self.work / "planted").write_text("stay")
        before = self.tree()
        head = self.head()
        written = self.record.stat().st_mtime_ns
        result = self.prepare("refine-1", "keep=yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tree(), before)
        self.assertEqual(self.head(), head)
        self.assertEqual(self.record.read_text(), "refine-1\n")
        self.assertEqual(self.record.stat().st_mtime_ns, written)

    def prepare(self, *args):
        return subprocess.run(
            ["just", "prepare", *args],
            cwd=ROOT,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def git(self, *args):
        return subprocess.run(
            [self.real_git, "-C", str(self.work), *args],
            capture_output=True,
            text=True,
        )

    def commits(self):
        result = self.git("log", "--format=%s")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.splitlines()

    def head(self):
        result = self.git("rev-parse", "HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def root_commit(self):
        result = self.git("rev-list", "--max-parents=0", "HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def tree(self):
        found = []
        if not self.work.exists():
            return found
        for path in sorted(self.work.rglob("*")):
            if ".git" in path.parts or not path.is_file():
                continue
            found.append((str(path.relative_to(self.work)), path.read_bytes()))
        return found

    def git_invocations(self):
        if not self.git_log.exists():
            return []
        return self.git_log.read_text().splitlines()

    def git_subcommands(self):
        found = []
        for line in self.git_invocations():
            words = line.split()
            if len(words) >= 3 and words[0] == "-C":
                found.append(words[2])
            elif words:
                found.append(words[0])
        return found

    def names(self, path):
        if not path.exists():
            return None
        return tuple(sorted(child.name for child in path.iterdir()))

    def assert_this_clone_untouched(self):
        self.assertEqual(self.names(self.real_develop), self.develop_before)
        if self.record_before is None:
            self.assertFalse(self.real_record.exists())
        else:
            self.assertEqual(self.real_record.read_bytes(), self.record_before)
