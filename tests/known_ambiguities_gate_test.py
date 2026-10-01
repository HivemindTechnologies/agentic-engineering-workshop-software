import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "pre-commit"


class KnownAmbiguitiesGate(unittest.TestCase):
    def test_hook_is_still_executable_and_names_no_claude_or_develop(self):
        text = HOOK.read_text()
        mode = HOOK.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)
        self.assertNotIn("claude", text)
        self.assertNotIn("develop/", text)

    def test_ambiguity_check_runs_after_spec_check_and_before_smooth(self):
        text = HOOK.read_text()
        spec_check = text.index("scripts/spec-check")
        ambiguity = text.index("scripts/ambiguity-check")
        drift = text.index("scripts/prompt-distance")
        smooth = text.index('"$root/scripts/lesson-status" smooth')
        self.assertLess(spec_check, ambiguity)
        self.assertLess(ambiguity, drift)
        self.assertLess(drift, smooth)

    def test_a_failed_ambiguity_check_stops_before_drift_and_smooth(self):
        repo = self.stage()
        self.write_script(repo, "spec-check", 0)
        self.write_script(repo, "ambiguity-check", 1)
        self.write_script(repo, "prompt-distance", 0)
        self.write_script(repo, "lesson-status", 0)
        result = self.run_hook(repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((repo / "ambiguity-check.ran").exists())
        self.assertFalse((repo / "prompt-distance.ran").exists())
        self.assertFalse((repo / "lesson-status.ran").exists())

    def test_a_failed_drift_check_stops_before_smooth(self):
        repo = self.stage()
        self.write_script(repo, "spec-check", 0)
        self.write_script(repo, "ambiguity-check", 0)
        self.write_script(repo, "prompt-distance", 1)
        self.write_script(repo, "lesson-status", 0)
        (repo / "workshop" / "prompt-distance-baseline.txt").write_text("refine-1 previous= absent next=+1.0000\n")
        result = self.run_hook(repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((repo / "prompt-distance.ran").exists())
        self.assertFalse((repo / "lesson-status.ran").exists())

    def test_a_missing_baseline_skips_the_drift_check_and_still_runs_smooth(self):
        repo = self.stage()
        self.write_script(repo, "spec-check", 0)
        self.write_script(repo, "ambiguity-check", 0)
        self.write_script(repo, "prompt-distance", 1)
        self.write_script(repo, "lesson-status", 0)
        result = self.run_hook(repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((repo / "prompt-distance.ran").exists())
        self.assertTrue((repo / "lesson-status.ran").exists())

    def test_everything_passing_runs_all_four_in_order(self):
        repo = self.stage()
        self.write_script(repo, "spec-check", 0)
        self.write_script(repo, "ambiguity-check", 0)
        self.write_script(repo, "prompt-distance", 0)
        self.write_script(repo, "lesson-status", 0)
        (repo / "workshop" / "prompt-distance-baseline.txt").write_text("refine-1 previous= absent next=+1.0000\n")
        result = self.run_hook(repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("ambiguity-check", "prompt-distance", "lesson-status"):
            self.assertTrue((repo / f"{name}.ran").exists())

    def stage(self):
        repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        hooks = repo / "hooks"
        hooks.mkdir()
        shutil.copy(HOOK, hooks / "pre-commit")
        os.chmod(hooks / "pre-commit", 0o755)
        (repo / "scripts").mkdir()
        (repo / "docs" / "specs").mkdir(parents=True)
        (repo / "workshop" / "material").mkdir(parents=True)
        (repo / "workshop" / "results").mkdir(parents=True)
        (repo / "workshop" / "JOURNEY.md").write_text("# refine-1: First\n")
        (repo / "workshop" / "known-ambiguities.txt").write_text("")
        bindir = repo / "bin"
        bindir.mkdir()
        (bindir / "just").write_text("#!/bin/sh\nexit 0\n")
        os.chmod(bindir / "just", 0o755)
        self.bindir = bindir
        return repo

    def write_script(self, repo, name, exit_code):
        script = repo / "scripts" / name
        script.write_text(f"#!/bin/sh\ntouch \"$REPO/{name}.ran\"\nexit {exit_code}\n")
        os.chmod(script, 0o755)

    def run_hook(self, repo):
        env = os.environ.copy()
        env["PATH"] = str(self.bindir) + os.pathsep + env["PATH"]
        env["REPO"] = str(repo)
        return subprocess.run([str(repo / "hooks" / "pre-commit")], capture_output=True, text=True, env=env)


if __name__ == "__main__":
    unittest.main()
