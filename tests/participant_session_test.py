import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "scripts" / "participant-session"
AGENT = ROOT / ".claude" / "agents" / "participant.md"
JUSTFILE = ROOT / "justfile"

FAKE = textwrap.dedent(
    """\
    import json, os, sys
    from pathlib import Path
    work = Path(os.environ["WORK"])
    expect = os.environ.get("EXPECT", "")
    create_on = int(os.environ.get("CREATE_ON", "0"))
    seen = 0
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        seen += 1
        if create_on and seen == create_on and expect:
            path = work / expect
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("ok\\n")
        sys.stdout.write(json.dumps({"type": "result", "num_turns": seen}) + "\\n")
        sys.stdout.flush()
    """
)


def run(*args, env=None):
    return subprocess.run([str(SESSION), *args], capture_output=True, text=True, env=env)


class WallClock(unittest.TestCase):
    def test_elapsed_time_rounds_up_to_the_next_whole_second(self):
        namespace = {"__name__": "participant_session"}
        exec(SESSION.read_text(), namespace)
        self.assertEqual(namespace["rounded_up"](0.1), 1)
        self.assertEqual(namespace["rounded_up"](2.0), 2)
        self.assertEqual(namespace["rounded_up"](2.01), 3)


class AgentFile(unittest.TestCase):
    def test_definition_is_the_generic_participant(self):
        text = AGENT.read_text()
        self.assertIn("name: participant\n", text)
        self.assertIn("description:", text)
        self.assertIn("permissionMode: bypassPermissions\n", text)
        self.assertNotIn("maxTurns", text)
        body = text.split("---", 2)[2]
        self.assertIn("Execute the lesson prompt", body)
        self.assertIn("Follow the recommendations", body)
        self.assertIn("working directory", body)
        for forbidden in ("workshop/", "workshop/results", "verdict: pass", "verdict: fail"):
            self.assertNotIn(forbidden, body)

    def test_install_copies_into_the_sandbox_tree(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        result = run("install", "--from", str(AGENT), "--work", str(work))
        self.assertEqual(result.returncode, 0, result.stderr)
        copied = (work / ".claude" / "agents" / "participant.md").read_text()
        self.assertEqual(copied, AGENT.read_text())


class LessonSection(unittest.TestCase):
    def test_section_includes_the_prompt_and_the_observations(self):
        journey = ROOT / "workshop" / "JOURNEY.md"
        result = run("section", str(journey), "refine-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("*PROMPT TO TEST*", result.stdout)
        self.assertIn("*EXPECTED OBSERVATIONS*", result.stdout)
        self.assertIn("No color, no table, no Markdown.", result.stdout)
        self.assertNotIn("# refine-1a:", result.stdout)


class OneSession(unittest.TestCase):
    def test_no_max_sends_one_message_and_closes_stdin(self):
        work, log, proc = self.launch(max_turns=None, create_on=0)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        messages = self.results(log)
        self.assertEqual([event["num_turns"] for event in messages], [1])
        self.assertNotIn('"type": "capped"', log.read_text())
        self.assertFalse((work / "docs" / "specs" / "out.md").exists())

    def test_max_stops_when_the_expected_file_appears(self):
        work, log, proc = self.launch(max_turns=3, create_on=2)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([event["num_turns"] for event in self.results(log)], [1, 2])
        self.assertTrue((work / "docs" / "specs" / "out.md").is_file())
        self.assertNotIn('"type": "capped"', log.read_text())

    def test_max_caps_and_records_one_log(self):
        work, log, proc = self.launch(max_turns=2, create_on=0)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([event["num_turns"] for event in self.results(log)], [1, 2])
        self.assertIn('{"type": "capped"}', log.read_text())
        self.assertFalse((work / "docs" / "specs" / "out.md").exists())
        measures = subprocess.run(
            [str(ROOT / "scripts" / "lesson-status"), "measures", str(log)],
            capture_output=True,
            text=True,
        )
        self.assertRegex(
            measures.stdout,
            r"^interactions=2 length=absent wall_seconds=[1-9][0-9]* capped=yes\n$",
        )

    def test_max_flag_is_rejected(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        result = run(
            "run",
            "--work",
            str(work),
            "--log",
            str(work / "session.jsonl"),
            "--message",
            "lesson",
            "--max",
            "2",
            "--",
            "python3",
            "-c",
            "print('ran')",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("use depth=", result.stderr)
        self.assertFalse((work / "session.jsonl").exists())

    def test_validate_recipe_passes_max_into_one_session(self):
        text = JUSTFILE.read_text()
        self.assertIn("--agent participant", text)
        self.assertNotIn("max is v6.M5", text)

    def launch(self, max_turns, create_on):
        work = Path(self.enterContext(tempfile.TemporaryDirectory()))
        log = work / "session.jsonl"
        fake = work / "fake.py"
        fake.write_text(FAKE)
        args = [
            "run",
            "--work",
            str(work),
            "--log",
            str(log),
            "--message",
            "lesson section",
            "--expect",
            "docs/specs/out.md",
        ]
        if max_turns is not None:
            args += ["--depth", str(max_turns)]
        env = os.environ.copy()
        env["WORK"] = str(work)
        env["EXPECT"] = "docs/specs/out.md"
        env["CREATE_ON"] = str(create_on)
        args += ["--", "python3", str(fake)]
        return work, log, run(*args, env=env)

    def results(self, log):
        return [
            json.loads(line)
            for line in log.read_text().splitlines()
            if line.startswith("{") and json.loads(line).get("type") == "result"
        ]


if __name__ == "__main__":
    unittest.main()
