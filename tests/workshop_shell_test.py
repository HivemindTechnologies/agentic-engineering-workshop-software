import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNER = ROOT / "workshop" / "banner.txt"
BANNER_SCRIPT = ROOT / "scripts" / "banner"
JUSTFILE = ROOT / "justfile"
FLAKE = ROOT / "flake.nix"
STATUS = ROOT / "scripts" / "lesson-status"
SPEC = "docs/specs/SPEC.v1-todo-list-cli-mvp.md"

ART = """\
 ██╗  ██╗██╗██╗   ██╗███████╗███╗   ███╗██╗███╗   ██╗██████╗
 ██║  ██║██║██║   ██║██╔════╝████╗ ████║██║████╗  ██║██╔══██╗
 ███████║██║██║   ██║█████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║
 ██╔══██║██║╚██╗ ██╔╝██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
 ██║  ██║██║ ╚████╔╝ ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
                              agentic engineering workshop
"""
ART_BLOCK = "\n".join(ART.splitlines()[:6]) + "\n"


def framed(kind):
    result = subprocess.run([str(BANNER_SCRIPT), kind], capture_output=True, text=True)
    return result


class BannerFile(unittest.TestCase):
    def test_banner_file_matches_the_spec_art(self):
        self.assertEqual(BANNER.read_text(), ART)

    def test_script_frames_art_with_kind_left_and_right(self):
        result = framed("sandbox")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("\n" + ART_BLOCK), result.stdout[:120])
        after = result.stdout[len("\n" + ART_BLOCK) :]
        subtitle, rest = after.split("\n", 1)
        self.assertTrue(subtitle.startswith("agentic engineering workshop"), subtitle)
        self.assertTrue(subtitle.endswith("sandbox"), subtitle)
        self.assertEqual(len(subtitle), len(ART.splitlines()[0]))
        self.assertEqual(rest, "\n")
        missing = subprocess.run([str(BANNER_SCRIPT)], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)


class OuterJust(unittest.TestCase):
    def test_default_prints_banner_outer_tag_and_list(self):
        listed = subprocess.run(["just", "--list"], cwd=ROOT, capture_output=True, text=True, check=True)
        result = subprocess.run(["just"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = framed("outer shell").stdout
        self.assertTrue(result.stdout.startswith(expected), result.stdout[:120])
        self.assertEqual(result.stdout[len(expected) :], listed.stdout)


class DevelopAndSandbox(unittest.TestCase):
    def test_flake_shell_hook_prints_banner_and_sandbox(self):
        text = FLAKE.read_text()
        self.assertIn('"$PWD/scripts/banner" "develop shell"', text)
        self.assertIn("yq-go", text)
        hook = text.split("shellHook = ''", 1)[1].split("'';", 1)[0]
        self.assertNotIn("python", hook)
        self.assertNotIn("yq", hook.replace("yq-go", ""))

    def test_sandbox_recipe_prints_banner_before_the_shell(self):
        shown = subprocess.run(["just", "--show", "sandbox"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("scripts/banner", shown.stdout)
        self.assertIn("sandbox shell", shown.stdout)
        self.assertNotIn("python", shown.stdout)
        self.assertNotIn("yq", shown.stdout)


class PrepareFrame(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.work = self.tmp / "develop"
        self.record = self.tmp / "prepared-lesson"
        self.env = os.environ.copy()
        self.env["PREPARE_WORK"] = str(self.work)
        self.env["PREPARE_RECORD"] = str(self.record)
        self.env["GIT_AUTHOR_NAME"] = "Prepare"
        self.env["GIT_AUTHOR_EMAIL"] = "prepare@example.com"
        self.env["GIT_COMMITTER_NAME"] = "Prepare"
        self.env["GIT_COMMITTER_EMAIL"] = "prepare@example.com"

    def test_prepare_frames_the_lesson_with_blank_lines_and_banner(self):
        result = subprocess.run(
            ["just", "prepare", "refine-1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        frame = framed("prepare").stdout
        self.assertIn(frame + "# refine-1:", result.stdout)
        shown = subprocess.run(["just", "--show", "prepare"], cwd=ROOT, capture_output=True, text=True)
        self.assertIn("scripts/banner", shown.stdout)
        self.assertNotIn("python", shown.stdout)
        self.assertNotIn("python3", shown.stdout)
        self.assertNotIn("yq", shown.stdout)


class RuntimeHeading(unittest.TestCase):
    def test_heading_writes_runtime_and_token_lines(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        journey = root / "JOURNEY.md"
        journey.write_text("# refine-1: First\n\nbody\n")
        lesson = root / "refine-1"
        stamp = "2026-09-28-02-00-00"
        (lesson / stamp / SPEC).parent.mkdir(parents=True)
        (lesson / stamp / SPEC).write_text("# spec\n")
        (lesson / "cutoff").write_text("2026-09-28-01-00-00\n")
        (lesson / stamp / "session.jsonl").write_text(
            '{"type": "result", "num_turns": 1, "usage": {"input_tokens": 900, "output_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}\n'
            '{"type": "wall", "wall_seconds": 90}\n'
        )
        (lesson / "judgements").mkdir()
        (lesson / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        result = subprocess.run(
            [str(STATUS), "heading", str(journey), str(root), "refine-1"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        text = journey.read_text()
        self.assertIn("# refine-1: First (last: PASS 2026-09-28-02-00-00)\n", text)
        self.assertIn("Minimum Runtime: 01:30\n", text)
        self.assertIn("Last Token Usage: 1.0k\n", text)
        self.assertIn("[Results](workshop/results/refine-1/2026-09-28-02-00-00)\n", text)
        self.assertIn("[Material](workshop/material/00-base/)\n", text)
        self.assertIn("[develop](develop/)\n", text)
        self.assertIn("body", text)
        again = subprocess.run(
            [str(STATUS), "heading", str(journey), str(root), "refine-1"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(journey.read_text().count("Minimum Runtime:"), 1)
        self.assertEqual(journey.read_text().count("Last Token Usage:"), 1)
        self.assertEqual(journey.read_text().count("[Results]("), 1)
        self.assertEqual(journey.read_text().count("[develop]("), 1)

    def test_heading_omits_runtime_when_wall_is_absent(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        journey = root / "JOURNEY.md"
        journey.write_text("# refine-1: First\n")
        lesson = root / "refine-1"
        stamp = "2026-09-28-02-00-00"
        (lesson / stamp / SPEC).parent.mkdir(parents=True)
        (lesson / stamp / SPEC).write_text("# spec\n")
        (lesson / "cutoff").write_text("2026-09-28-01-00-00\n")
        (lesson / stamp / "session.jsonl").write_text(
            '{"type": "result", "num_turns": 1, "usage": {"input_tokens": 500, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}\n'
        )
        (lesson / "judgements").mkdir()
        (lesson / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        result = subprocess.run(
            [str(STATUS), "heading", str(journey), str(root), "refine-1"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        text = journey.read_text()
        self.assertNotIn("Minimum Runtime:", text)
        self.assertIn("Last Token Usage: 0.5k\n", text)


class StatusDisplay(unittest.TestCase):
    def test_status_write_is_silent_and_status_displays_with_yq(self):
        if shutil.which("yq") is None:
            self.skipTest("yq not on PATH")
        text = JUSTFILE.read_text()
        self.assertIn("status-write:", text)
        self.assertIn(
            'python3 scripts/lesson-status yaml "{{justfile_directory()}}/workshop/results" "{{justfile_directory()}}/workshop/results/status.yaml"',
            text,
        )
        validate = text.split("validate *lessons:", 1)[1].split("\nprompt-distance", 1)[0]
        self.assertIn('lesson-status" yaml', validate)
        before = (ROOT / "workshop" / "results" / "status.yaml").read_text()
        silent = subprocess.run(["just", "status-write"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(silent.returncode, 0, silent.stderr)
        self.assertEqual(silent.stdout, "")
        self.assertEqual((ROOT / "workshop" / "results" / "status.yaml").read_text(), before)
        shown = subprocess.run(["just", "status"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertTrue(shown.stdout.startswith("baseline_wall_seconds:"))
        self.assertEqual((ROOT / "workshop" / "results" / "status.yaml").read_text(), before)
        one = subprocess.run(["just", "status", "refine-1"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(one.returncode, 0, one.stderr)
        self.assertIn("lesson: refine-1", one.stdout)
        self.assertNotIn("lesson: refine-1a", one.stdout)
        missing = subprocess.run(["just", "status", "nope"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)


if __name__ == "__main__":
    unittest.main()
