import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "pre-commit"
INSTALL = ROOT / "scripts" / "install-hooks"
SPEC_CHECK = ROOT / "scripts" / "spec-check"
JUSTFILE = ROOT / "justfile"
VALID_SPEC = """# Fixture

## M1: One check (Status: PENDING)

**Acceptance Criteria:**

- The fixture is a spec.
"""


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)


class HookFile(unittest.TestCase):
    def test_hook_is_executable_and_its_first_check_is_just_test(self):
        text = HOOK.read_text()
        mode = HOOK.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)
        body = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        commands = [line for line in body if not line.startswith("set ") and not line.startswith("root=") and line != "cd \"$root\""]
        self.assertEqual(commands[0], "just test")
        self.assertNotIn("claude", text)
        self.assertNotIn("develop/", text)


class InstallHooks(unittest.TestCase):
    def test_sets_only_the_hooks_path_and_a_second_run_keeps_it(self):
        repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git(repo, "init")
        git(repo, "config", "user.email", "gate@example.com")
        git(repo, "config", "user.name", "Gate")
        before = set(git(repo, "config", "--local", "--list").stdout.splitlines())
        first = subprocess.run([str(INSTALL), str(repo)], capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        after = set(git(repo, "config", "--local", "--list").stdout.splitlines())
        self.assertEqual(after - before, {"core.hookspath=hooks"})
        self.assertEqual(git(repo, "config", "--get", "core.hooksPath").stdout.strip(), "hooks")
        second = subprocess.run([str(INSTALL), str(repo)], capture_output=True, text=True)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(git(repo, "config", "--get", "core.hooksPath").stdout.strip(), "hooks")
        self.assertEqual(git(repo, "config", "--get", "user.email").stdout.strip(), "gate@example.com")

    def test_just_recipe_points_this_clone_at_the_script(self):
        text = JUSTFILE.read_text()
        self.assertIn("install-hooks:", text)
        self.assertIn('scripts/install-hooks "{{justfile_directory()}}"', text)


class CommitGate(unittest.TestCase):
    def test_commit_is_rejected_when_just_test_fails_and_created_when_it_passes(self):
        rejected = self.repo(just_exit=1)
        denied = self.commit(rejected)
        self.assertNotEqual(denied.returncode, 0)
        self.assertNotEqual(git(rejected, "rev-parse", "--verify", "HEAD").returncode, 0)
        self.assertEqual((rejected / "just.log").read_text().splitlines(), ["test"])
        accepted = self.repo(just_exit=0)
        allowed = self.commit(accepted)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(git(accepted, "rev-parse", "--verify", "HEAD").returncode, 0)
        self.assertNotIn("claude", (accepted / "just.log").read_text())

    def repo(self, just_exit):
        repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git(repo, "init")
        git(repo, "config", "user.email", "gate@example.com")
        git(repo, "config", "user.name", "Gate")
        hooks = repo / "hooks"
        hooks.mkdir()
        shutil.copy(HOOK, hooks / "pre-commit")
        os.chmod(hooks / "pre-commit", 0o755)
        git(repo, "config", "core.hooksPath", "hooks")
        bindir = repo / "bin"
        bindir.mkdir()
        (bindir / "just").write_text(
            "#!/bin/sh\nprintf '%s\\n' \"$1\" >> \"$REPO/just.log\"\nexit \"$JUST_EXIT\"\n"
        )
        os.chmod(bindir / "just", 0o755)
        scripts = repo / "scripts"
        scripts.mkdir()
        (scripts / "lesson-status").write_text("#!/bin/sh\nexit 0\n")
        os.chmod(scripts / "lesson-status", 0o755)
        (scripts / "ambiguity-check").write_text("#!/bin/sh\nexit 0\n")
        os.chmod(scripts / "ambiguity-check", 0o755)
        (repo / "README.md").write_text("note\n")
        git(repo, "add", "README.md")
        self.bindir = bindir
        self.just_exit = just_exit
        return repo

    def commit(self, repo):
        env = os.environ.copy()
        env["PATH"] = str(self.bindir) + os.pathsep + env["PATH"]
        env["JUST_EXIT"] = str(self.just_exit)
        env["REPO"] = str(repo)
        return git(repo, "commit", "-m", "note", env=env)


class SpecCheckGate(unittest.TestCase):
    def test_v8_spec_passes_the_checker(self):
        result = subprocess.run(
            [str(SPEC_CHECK), str(ROOT / "docs" / "specs" / "SPEC.v8-quality-gates.md")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_failed_tests_skip_the_spec_checker_and_keep_their_status(self):
        repo = self.stage(just_exit=4)
        self.stub_spec_check(repo)
        (repo / "docs" / "specs" / "SPEC.one.md").write_text(VALID_SPEC)
        result = self.run_hook(repo)
        self.assertEqual(result.returncode, 4)
        self.assertFalse((repo / "specs.log").exists())

    def test_each_spec_is_checked_and_a_failure_is_the_checker_line_only(self):
        passing = self.stage(just_exit=0)
        self.stub_spec_check(passing)
        one = passing / "docs" / "specs" / "SPEC.one.md"
        two = passing / "docs" / "specs" / "SPEC.two.md"
        one.write_text(VALID_SPEC)
        two.write_text(VALID_SPEC)
        self.stub_lesson_status(passing, code=0)
        ok = self.run_hook(passing)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(ok.stdout, "")
        self.assertEqual((passing / "specs.log").read_text().splitlines(), [str(one), str(two)])
        failing = self.stage(just_exit=0)
        shutil.copy(SPEC_CHECK, failing / "scripts" / "spec-check")
        os.chmod(failing / "scripts" / "spec-check", 0o755)
        bad = failing / "docs" / "specs" / "SPEC.bad.md"
        bad.write_text("# Fixture\n\n## M1: Broken (Status: NOPE)\n\n**Acceptance Criteria:**\n\n- a\n")
        (failing / "docs" / "specs" / "SPEC.later.md").write_text(VALID_SPEC)
        denied = self.run_hook(failing)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(denied.stdout, "")
        self.assertEqual(denied.stderr.strip(), f"{bad}:3")

    def stage(self, just_exit):
        repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        hooks = repo / "hooks"
        hooks.mkdir()
        shutil.copy(HOOK, hooks / "pre-commit")
        os.chmod(hooks / "pre-commit", 0o755)
        (repo / "scripts").mkdir()
        (repo / "docs" / "specs").mkdir(parents=True)
        bindir = repo / "bin"
        bindir.mkdir()
        (bindir / "just").write_text("#!/bin/sh\nexit \"$JUST_EXIT\"\n")
        os.chmod(bindir / "just", 0o755)
        (repo / "scripts" / "ambiguity-check").write_text("#!/bin/sh\nexit 0\n")
        os.chmod(repo / "scripts" / "ambiguity-check", 0o755)
        repo.joinpath("just_exit").write_text(str(just_exit))
        return repo

    def stub_spec_check(self, repo):
        script = repo / "scripts" / "spec-check"
        script.write_text("#!/bin/sh\nprintf '%s\\n' \"$1\" >> \"$REPO/specs.log\"\nexit 0\n")
        os.chmod(script, 0o755)

    def stub_lesson_status(self, repo, code):
        script = repo / "scripts" / "lesson-status"
        script.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$REPO/smooth.log\"\nexit {code}\n")
        os.chmod(script, 0o755)

    def run_hook(self, repo):
        env = os.environ.copy()
        env["PATH"] = str(repo / "bin") + os.pathsep + env["PATH"]
        env["JUST_EXIT"] = (repo / "just_exit").read_text()
        env["REPO"] = str(repo)
        return subprocess.run([str(repo / "hooks" / "pre-commit")], capture_output=True, text=True, env=env)


class SmoothGate(unittest.TestCase):
    def test_a_failed_spec_does_not_read_a_judgement(self):
        repo = SpecCheckGate.stage(self, just_exit=0)
        script = repo / "scripts" / "spec-check"
        script.write_text("#!/bin/sh\necho 'docs/specs/SPEC.bad.md:3' >&2\nexit 1\n")
        os.chmod(script, 0o755)
        (repo / "docs" / "specs" / "SPEC.bad.md").write_text("bad\n")
        SpecCheckGate.stub_lesson_status(self, repo, code=0)
        journey = repo / "workshop" / "JOURNEY.md"
        journey.parent.mkdir()
        journey.write_text("# refine-1: First\n")
        result = SpecCheckGate.run_hook(self, repo)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((repo / "smooth.log").exists())
        self.assertEqual(journey.read_text(), "# refine-1: First\n")
        self.assertNotIn("instruct", HOOK.read_text())

    def test_hook_stops_at_the_first_lesson_that_is_not_smooth(self):
        repo = SpecCheckGate.stage(self, just_exit=0)
        SpecCheckGate.stub_spec_check(self, repo)
        (repo / "docs" / "specs" / "SPEC.one.md").write_text(VALID_SPEC)
        shutil.copy(ROOT / "scripts" / "lesson-status", repo / "scripts" / "lesson-status")
        shutil.copy(ROOT / "scripts" / "journey.py", repo / "scripts" / "journey.py")
        os.chmod(repo / "scripts" / "lesson-status", 0o755)
        journey = repo / "workshop" / "JOURNEY.md"
        journey.parent.mkdir(parents=True, exist_ok=True)
        journey.write_text(
            "# refine-1: First\n\n# refine-1a: Second\n\n# refine-2: Third\n"
        )
        judged = repo / "workshop" / "results" / "refine-1a"
        judged.mkdir(parents=True)
        (judged / "JUDGE.md").write_text("# Judge\n")
        (judged / "judgements").mkdir()
        (judged / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: fail\n")
        (repo / "workshop" / "results" / "refine-2").mkdir()
        result = SpecCheckGate.run_hook(self, repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refine-1a not smooth", result.stdout)
        self.assertNotIn("refine-2", result.stdout)


class StatusRecipe(unittest.TestCase):
    def test_status_write_and_validate_write_the_same_file(self):
        text = JUSTFILE.read_text()
        self.assertIn(
            'python3 scripts/lesson-status yaml "{{justfile_directory()}}/workshop/results" "{{justfile_directory()}}/workshop/results/status.yaml"',
            text,
        )
        self.assertIn("status-write:", text)
        validate = text.split("validate *lessons:", 1)[1].split("\nprompt-distance", 1)[0]
        heading = validate.rindex("lesson-status\" heading")
        writer = validate.rindex("lesson-status\" yaml")
        exit_at = validate.rindex('exit "$status"')
        self.assertLess(heading, writer)
        self.assertLess(writer, exit_at)
        journey = (ROOT / "workshop" / "JOURNEY.md").read_text()
        result = subprocess.run(["just", "status-write"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("claude", result.stderr)
        self.assertEqual((ROOT / "workshop" / "JOURNEY.md").read_text(), journey)
        written = (ROOT / "workshop" / "results" / "status.yaml").read_text()
        self.assertTrue(written.startswith("baseline_wall_seconds:"))
        again = subprocess.run(["just", "status-write"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual((ROOT / "workshop" / "results" / "status.yaml").read_text(), written)
