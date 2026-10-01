"""outer.v15.M4-M5 — PMD CPD redundancy gate, skill, verbosity, suppression, quiet baseline, lesson."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
SCRIPT = APP / "scripts" / "check-redundancies"
CPD_PROJECT = APP / "scripts" / "check-redundancies-cpd"
SKILL = APP / ".claude" / "skills" / "check-redundancies" / "SKILL.md"
MATERIAL_SKILL = (
    ROOT / "workshop" / "material" / "quality-gates-4" / ".claude" / "skills" / "check-redundancies" / "SKILL.md"
)
REPORT_V4 = APP / "snapshots" / "redundancy-report-v4.json"
REPORT_QUIET = APP / "snapshots" / "redundancy-report-quiet.json"
BASELINE = APP / "snapshots" / "redundancy-baseline.json"
DUP = APP / "testdata" / "redundancy" / "dup"
SUP = APP / "testdata" / "redundancy" / "suppressed"
JOURNEY = ROOT / "workshop" / "JOURNEY.md"


def run_check(root: Path, report: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), str(root), "--report", str(report), *extra],
        capture_output=True,
        text=True,
        cwd=APP,
    )


def report_in(tmp: Path, name: str) -> Path:
    return tmp / name


class RedundancyGate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_the_tool_is_pmd_cpd_on_the_jvm_and_pinned(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertIn("bash", SCRIPT.read_text(encoding="utf-8").splitlines()[0])
        build = (CPD_PROJECT / "build.sbt").read_text(encoding="utf-8")
        self.assertIn('val pmdVersion = "7.28.0"', build)
        self.assertIn('"pmd-core"', build)
        self.assertIn('"pmd-scala_2.13"', build)
        self.assertTrue((CPD_PROJECT / "src" / "main" / "scala" / "CheckRedundancies.scala").is_file())

    def test_no_python_in_the_redundancy_path(self):
        for path in (
            SCRIPT,
            CPD_PROJECT / "build.sbt",
            CPD_PROJECT / "src" / "main" / "scala" / "CheckRedundancies.scala",
            SKILL,
            APP / "justfile",
        ):
            self.assertNotIn("python", path.read_text(encoding="utf-8").lower(), str(path))
        self.assertEqual(list(APP.rglob("check-redundancies*.py")), [])

    def test_first_report_and_snapshots_come_from_pmd_cpd(self):
        for path in (REPORT_V4, REPORT_QUIET, BASELINE):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["tool"], "pmd-cpd", path.name)
            self.assertEqual(data["version"], "7.28.0", path.name)
            self.assertEqual(data["root"], "src", path.name)
        self.assertGreater(json.loads(REPORT_V4.read_text())["finding_count"], 0)

    def test_skill_surfaces_ranking_refactors_and_region_suppression(self):
        for path in (SKILL, MATERIAL_SKILL):
            text = path.read_text(encoding="utf-8")
            self.assertIn("lines × occurrences", text)
            self.assertIn("PMD", text)
            self.assertIn("parameterize", text.lower())
            self.assertIn("abstraction", text.lower())
            self.assertIn("CPD-OFF", text)
            self.assertIn("redundancy", text.lower())
            self.assertIn("copy-paste", text.lower())

    def test_verbosity_levels_differ(self):
        quiet = report_in(self.tmp, "quiet.json")
        verbose = report_in(self.tmp, "verbose.json")
        self.assertEqual(run_check(DUP, quiet, "--verbosity", "quiet").returncode, 0)
        self.assertEqual(run_check(DUP, verbose, "--verbosity", "verbose").returncode, 0)
        q = json.loads(quiet.read_text())
        v = json.loads(verbose.read_text())
        self.assertGreater(q["finding_count"], 0)
        self.assertEqual(q["finding_count"], v["finding_count"])
        self.assertIn("snippet", v["findings"][0])
        self.assertNotIn("snippet", q["findings"][0])

    def test_the_default_is_quiet_enough_for_ci(self):
        result = run_check(DUP, report_in(self.tmp, "r.json"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "findings: 1")

    def test_findings_are_ranked_by_lines_times_occurrences(self):
        report = report_in(self.tmp, "r.json")
        run_check(APP / "testdata" / "redundancy", report, "--verbosity", "normal")
        findings = json.loads(report.read_text())["findings"]
        impact = [f["lines"] * f["occurrences"] for f in findings]
        self.assertEqual(impact, sorted(impact, reverse=True))

    def test_findings_fail_the_gate_only_when_asked(self):
        self.assertEqual(run_check(DUP, report_in(self.tmp, "a.json")).returncode, 0)
        self.assertEqual(run_check(DUP, report_in(self.tmp, "b.json"), "--fail-on-findings").returncode, 1)

    def test_a_cpd_off_region_suppresses_and_an_unsuppressed_duplicate_still_fails(self):
        ok = run_check(SUP, report_in(self.tmp, "sup.json"), "--fail-on-findings")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(json.loads((self.tmp / "sup.json").read_text())["finding_count"], 0)
        bad = run_check(DUP, report_in(self.tmp, "dup.json"), "--fail-on-findings")
        self.assertNotEqual(bad.returncode, 0)

    def test_an_allow_glob_excludes_a_path(self):
        result = run_check(DUP, report_in(self.tmp, "allow.json"), "--allow", "**/B.scala", "--fail-on-findings")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_known_limit_a_renamed_copy_is_not_reported_and_the_unsupported_flag_is_rejected(self):
        # PMD's Scala CPD compares tokens verbatim; --ignore-identifiers has no effect there, so the
        # tool does not offer it. A copy with every identifier renamed is out of reach of this gate.
        renamed = self.tmp / "renamed"
        renamed.mkdir()
        body = "    val {a} = x + 1\n    val {b} = {a} * 2\n    val {c} = {b} - 3\n    val {d} = {c} + 4\n"
        body += "    val {e} = {d} * 5\n    val {f} = {e} - 6\n    val {g} = {f} + 7\n    val {h} = {g} * 8\n    {f} + {h}\n"
        (renamed / "A.scala").write_text(
            "object A:\n  def one(x: Int): Int =\n" + body.format(a="a", b="b", c="c", d="d", e="e", f="f", g="g", h="h")
        )
        (renamed / "B.scala").write_text(
            "object B:\n  def two(x: Int): Int =\n"
            + body.format(a="p", b="q", c="r", d="s", e="t", f="u", g="v", h="w")
        )
        plain = run_check(renamed, report_in(self.tmp, "plain.json"), "--fail-on-findings")
        self.assertEqual(plain.returncode, 0, "renamed identifiers differ token-for-token")
        rejected = run_check(renamed, report_in(self.tmp, "loose.json"), "--ignore-identifiers")
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("unknown flag: --ignore-identifiers", rejected.stderr)

    def test_the_pre_fix_app_v4_report_recorded_findings(self):
        data = json.loads(REPORT_V4.read_text(encoding="utf-8"))
        files = {loc["file"] for f in data["findings"] for loc in f["locations"]}
        self.assertIn("main/scala/todo/Cli.scala", files)

    def test_quiet_baseline_on_app(self):
        for path in (REPORT_QUIET, BASELINE):
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["finding_count"], 0)
        result = run_check(APP / "src", report_in(self.tmp, "app.json"), "--fail-on-findings")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.tmp / "app.json").read_text())["finding_count"], 0)

    def test_quality_gates_4_lesson(self):
        journey = JOURNEY.read_text(encoding="utf-8")
        self.assertIn("quality-gates-4", journey)
        self.assertIn("redundancy", journey.lower())
        self.assertTrue((ROOT / "workshop" / "material" / "quality-gates-4" / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
