import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "scripts" / "lesson-status"
SPEC = "docs/specs/SPEC.v1-todo-list-cli-mvp.md"
LESSONS = (
    "refine-1",
    "refine-1a",
    "refine-2",
    "refine-3",
    "refine-4",
    "refine-5",
    "refine-6",
    "implement-1",
    "implement-1b",
    "implement-2",
    "quality-gates-1",
    "refine-7",
    "quality-gates-2",
    "skills-1",
    "skills-2",
)
JOURNEY = "".join(f"# {lesson}: Title\n\n" for lesson in LESSONS)


def write_journey(root):
    (root / "JOURNEY.md").write_text(JOURNEY)
    return root


def run(*args):
    return subprocess.run([str(STATUS), *args], capture_output=True, text=True)


def result_event(turns, usage):
    event = {"type": "result", "num_turns": turns}
    if usage is not None:
        event["usage"] = usage
    return event


def usage(input_tokens, output_tokens, cache_creation, cache_read):
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
    }


class TraceMetrics(unittest.TestCase):
    def test_known_turns_and_usage(self):
        path = self.log(
            [
                {"type": "assistant"},
                result_event(4, usage(10, 3, 100, 7)),
            ]
        )
        first = run("measures", str(path))
        second = run("measures", str(path))
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, "interactions=4 length=120 wall_seconds=absent\n")
        self.assertEqual(second.stdout, first.stdout)
        self.assertNotIn("capped", first.stdout)

    def test_missing_usage_is_absent_not_zero(self):
        path = self.log([{"type": "assistant"}, {"type": "assistant"}, result_event(2, None)])
        result = run("measures", str(path))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "interactions=2 length=absent wall_seconds=absent\n")

    def test_counts_assistant_events_when_num_turns_is_absent(self):
        path = self.log(
            [
                {"type": "assistant"},
                {"type": "user"},
                {"type": "assistant"},
                {"type": "result", "usage": usage(1, 1, 0, 0)},
            ]
        )
        result = run("measures", str(path))
        self.assertEqual(result.stdout, "interactions=2 length=2 wall_seconds=absent\n")

    def test_capped_marker_is_recorded(self):
        path = self.log(
            [
                result_event(3, usage(1, 1, 0, 0)),
                {"type": "capped"},
            ]
        )
        result = run("measures", str(path))
        self.assertEqual(result.stdout, "interactions=3 length=2 wall_seconds=absent capped=yes\n")

    def test_known_wall_seconds_is_stable_and_not_a_failure(self):
        path = self.log(
            [
                result_event(4, usage(10000, 2000, 40, 3)),
                {"type": "wall", "wall_seconds": 90},
            ]
        )
        first = run("measures", str(path))
        second = run("measures", str(path))
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, "interactions=4 length=12043 wall_seconds=90\n")
        self.assertEqual(second.stdout, first.stdout)

    def log(self, events):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = directory / "session.jsonl"
        path.write_text("".join(json.dumps(event) + "\n" for event in events))
        return path


class LessonLine(unittest.TestCase):
    def test_pass_line_includes_measures(self):
        root = self.tree(
            "refine-1",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": True,
                    "session": [result_event(4, usage(10000, 2000, 40, 3))],
                }
            },
            judgement=("2026-09-28-03-00-00", "verdict: pass\n"),
        )
        result = run("lines", str(root), "refine-1")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout,
            "refine-1     PASS interactions=4 length=12043 wall_seconds=absent\nbaseline wall_seconds=0\n",
        )

    def test_missing_spec_is_fail_simulate_and_keeps_measures(self):
        root = self.tree(
            "refine-1a",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": False,
                    "session": [result_event(6, None)],
                }
            },
        )
        result = run("lines", str(root), "refine-1a")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            "refine-1a    FAIL simulate interactions=6 length=absent wall_seconds=absent\nbaseline wall_seconds=0\n",
        )

    def test_one_tree_with_a_fail_verdict_is_fail_judge(self):
        root = self.tree(
            "refine-2",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": True,
                    "session": [result_event(1, usage(1, 0, 0, 0))],
                }
            },
            judgement=("2026-09-28-03-00-00", "notes\nverdict: fail\n"),
        )
        result = run("lines", str(root), "refine-2")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            "refine-2     FAIL judge interactions=1 length=1 wall_seconds=absent\nbaseline wall_seconds=0\n",
        )

    def test_not_started_omits_measures(self):
        root = self.tree("refine-3", cutoff="", stamps={})
        result = run("lines", str(root), "refine-3")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "refine-3     not run\nbaseline wall_seconds=0\n")

    def test_not_run_keeps_measures_when_a_stamp_has_a_session(self):
        root = self.tree(
            "refine-5",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": False,
                    "session": [result_event(2, usage(3, 0, 0, 0))],
                }
            },
        )
        result = run("lines", str(root), "refine-5")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            "refine-5     FAIL simulate interactions=2 length=3 wall_seconds=absent\nbaseline wall_seconds=0\n",
        )

    def test_lines_follow_journey_order_and_do_not_stop(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.add(root, "refine-1", "2026-09-28-02-00-00", spec=False, events=[result_event(1, usage(1, 0, 0, 0))])
        self.add(root, "refine-1a", "2026-09-28-02-00-00", spec=True, events=[result_event(1, usage(1, 0, 0, 0))])
        (root / "refine-1a" / "judgements").mkdir()
        (root / "refine-1a" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        result = run("lines", str(root))
        lesson_lines = [line for line in result.stdout.splitlines() if not line.startswith("baseline ")]
        names = [line.split()[0] for line in lesson_lines]
        self.assertTrue(result.stdout.splitlines()[-1].startswith("baseline wall_seconds="))
        self.assertEqual(
            names,
            list(LESSONS),
        )
        self.assertIn("FAIL simulate", result.stdout.splitlines()[0])
        self.assertIn("PASS", result.stdout.splitlines()[1])
        self.assertEqual(result.returncode, 1)

    def test_heading_writes_the_status_and_the_newest_tree_stamp(self):
        root = self.tree(
            "refine-1",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": True,
                    "session": [result_event(1, usage(1, 0, 0, 0))],
                }
            },
            judgement=("2026-09-28-03-00-00", "verdict: pass\n"),
        )
        journey = root / "JOURNEY.md"
        journey.write_text("# refine-1: First (last: FAIL judge 2026-09-28-01-00-00)\n\nbody\n")
        result = run("heading", str(journey), str(root), "refine-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = journey.read_text()
        self.assertIn("# refine-1: First (last: PASS 2026-09-28-02-00-00)\n", text)
        self.assertEqual(text.count("(last:"), 1)
        self.assertIn("body", text)

    def test_smooth_stops_at_the_first_judged_lesson_that_is_not_pass(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        (root / "refine-1a").mkdir()
        (root / "refine-1a" / "JUDGE.md").write_text("# Judge\n")
        (root / "refine-1a" / "judgements").mkdir()
        (root / "refine-1a" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: fail\n")
        (root / "refine-2").mkdir()
        result = run("smooth", str(root))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "refine-1 not yet judged\nrefine-1a not smooth\n")
        self.assertNotIn("refine-2", result.stdout)

    def test_smooth_passes_and_reports_lessons_that_have_no_judge(self):
        root = self.tree(
            "refine-1",
            cutoff="2026-09-28-01-00-00",
            stamps={
                "2026-09-28-02-00-00": {
                    "spec": True,
                    "session": [result_event(1, usage(1, 0, 0, 0))],
                }
            },
            judgement=("2026-09-28-03-00-00", "verdict: pass\n"),
        )
        (root / "refine-1" / "JUDGE.md").write_text("# Judge\n")
        result = run("smooth", str(root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "\n".join(f"{lesson} not yet judged" for lesson in LESSONS[1:]) + "\n",
        )

    def test_heading_without_a_tree_has_no_stamp(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        journey = root / "JOURNEY.md"
        journey.write_text("# refine-3: Later\n")
        result = run("heading", str(journey), str(root), "refine-3")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = journey.read_text()
        self.assertIn("# refine-3: Later (last: not run)\n", text)
        self.assertIn("[Results](workshop/results/refine-3/)\n", text)
        self.assertIn("[Material](workshop/material/00-base/)\n", text)
        self.assertIn("[develop](develop/)\n", text)
        self.assertNotIn("Minimum Runtime:", text)

    def test_verdict_is_the_newest_in_range_line_and_is_not_a_failure(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        lesson = root / "refine-4"
        (lesson / "judgements").mkdir(parents=True)
        (lesson / "cutoff").write_text("2026-09-28-02-00-00\n")
        (lesson / "judgements" / "2026-09-28-01-00-00.md").write_text("verdict: pass\n")
        (lesson / "judgements" / "2026-09-28-03-00-00.md").write_text("notes\nverdict: fail\n")
        result = run("verdict", str(root), "refine-4")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "fail\n")
        self.assertEqual(run("verdict", str(root), "refine-4").stdout, result.stdout)

    def test_verdict_is_absent_when_none_is_in_range(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        lesson = root / "refine-4"
        (lesson / "judgements").mkdir(parents=True)
        (lesson / "cutoff").write_text("2026-09-28-02-00-00\n")
        (lesson / "judgements" / "2026-09-28-01-00-00.md").write_text("verdict: pass\n")
        result = run("verdict", str(root), "refine-4")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "absent\n")

    def test_verdict_rejects_an_unknown_lesson(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        result = run("verdict", str(root), "nope")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown lesson: nope", result.stderr)

    def test_baseline_sums_recorded_seconds_and_skips_absent(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        self.add(
            root,
            "refine-1",
            "2026-09-28-02-00-00",
            spec=True,
            events=[result_event(4, usage(1, 0, 0, 0)), {"type": "wall", "wall_seconds": 90}],
        )
        self.add(
            root,
            "refine-1a",
            "2026-09-28-02-00-00",
            spec=True,
            events=[result_event(1, usage(1, 0, 0, 0))],
        )
        (root / "refine-1" / "judgements").mkdir()
        (root / "refine-1" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        (root / "refine-1a" / "judgements").mkdir()
        (root / "refine-1a" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        result = run("lines", str(root))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("refine-1     PASS interactions=4 length=1 wall_seconds=90", result.stdout)
        self.assertIn("refine-1a    PASS interactions=1 length=1 wall_seconds=absent", result.stdout)
        self.assertEqual(result.stdout.splitlines()[-1], "baseline wall_seconds=90")

    def tree(self, lesson, cutoff, stamps, judgement=None):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        for stamp, body in stamps.items():
            self.add(root, lesson, stamp, body["spec"], body["session"], cutoff=cutoff)
        if judgement is not None:
            stamp, text = judgement
            folder = root / lesson / "judgements"
            folder.mkdir(parents=True)
            (folder / f"{stamp}.md").write_text(text)
        return root

    def add(self, root, lesson, stamp, spec, events, cutoff="2026-09-28-01-00-00"):
        if not (root / "JOURNEY.md").is_file():
            write_journey(root)
        lesson_dir = root / lesson
        lesson_dir.mkdir(parents=True, exist_ok=True)
        if cutoff:
            (lesson_dir / "cutoff").write_text(cutoff + "\n")
        tree = lesson_dir / stamp
        if spec:
            spec_path = tree / SPEC
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text("# spec\n")
        else:
            tree.mkdir(parents=True)
        (tree / "session.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))


class StatusFile(unittest.TestCase):
    def test_yaml_matches_the_newest_run_and_a_second_write_is_identical(self):
        root = write_journey(Path(self.enterContext(tempfile.TemporaryDirectory())))
        self.add(
            root,
            "refine-1",
            "2026-09-28-02-00-00",
            spec=True,
            events=[result_event(4, usage(10000, 2000, 40, 3)), {"type": "wall", "wall_seconds": 90}],
        )
        (root / "refine-1" / "judgements").mkdir()
        (root / "refine-1" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        self.add(
            root,
            "refine-1a",
            "2026-09-28-02-00-00",
            spec=True,
            events=[result_event(1, usage(1, 0, 0, 0)), {"type": "capped"}],
        )
        (root / "refine-1a" / "judgements").mkdir()
        (root / "refine-1a" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: fail\n")
        dest = root / "status.yaml"
        first = run("yaml", str(root), str(dest))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, "")
        text = dest.read_text()
        self.assertEqual(text, EXPECTED_STATUS)
        second = run("yaml", str(root), str(dest))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(dest.read_text(), text)

    def test_a_missing_wall_record_is_null_and_adds_nothing_to_the_baseline(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.add(
            root,
            "refine-1",
            "2026-09-28-02-00-00",
            spec=True,
            events=[result_event(4, usage(1, 0, 0, 0))],
        )
        (root / "refine-1" / "judgements").mkdir()
        (root / "refine-1" / "judgements" / "2026-09-28-03-00-00.md").write_text("verdict: pass\n")
        dest = root / "status.yaml"
        result = run("yaml", str(root), str(dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        text = dest.read_text()
        self.assertTrue(text.startswith("baseline_wall_seconds: 0\n"))
        self.assertIn("    wall_seconds: null\n", text)
        self.assertNotIn("\n    wall_seconds: 0\n", text)

    def add(self, root, lesson, stamp, spec, events, cutoff="2026-09-28-01-00-00"):
        LessonLine.add(self, root, lesson, stamp, spec, events, cutoff)


NOT_RUN = """  - lesson: {lesson}
    status: "not run"
    stamp: null
    verdict: null
    interactions: null
    length: null
    wall_seconds: null
    capped: false
"""

EXPECTED_STATUS = (
    "baseline_wall_seconds: 90\n"
    "lessons:\n"
    "  - lesson: refine-1\n"
    "    status: PASS\n"
    "    stamp: 2026-09-28-02-00-00\n"
    "    verdict: pass\n"
    "    interactions: 4\n"
    "    length: 12043\n"
    "    wall_seconds: 90\n"
    "    capped: false\n"
    "  - lesson: refine-1a\n"
    '    status: "FAIL judge"\n'
    "    stamp: 2026-09-28-02-00-00\n"
    "    verdict: fail\n"
    "    interactions: 1\n"
    "    length: 1\n"
    "    wall_seconds: null\n"
    "    capped: true\n"
    + "".join(NOT_RUN.format(lesson=lesson) for lesson in LESSONS[2:])
)


if __name__ == "__main__":
    unittest.main()
