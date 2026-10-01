import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "spec-check"
SCALA = ROOT / "scripts" / "spec-check-scala" / "run"
SCALA_PROJECT = ROOT / "scripts" / "spec-check-scala"
SPECS = [
    ROOT / "docs" / "specs" / "SPEC.v1-onion-layering.md",
    ROOT / "docs" / "specs" / "SPEC.v2-simulation.md",
    ROOT / "docs" / "specs" / "SPEC.v3-judge.md",
    ROOT / "docs" / "specs" / "SPEC.v4-journey.md",
    ROOT / "docs" / "specs" / "SPEC.v5-sdd-overhaul.md",
    ROOT / "docs" / "specs" / "SPEC.v6-interactive-tracked-participant-subagent.md",
    ROOT / "docs" / "specs" / "SPEC.v7-instructor-subagent.md",
]

GOOD_BODY = "\n".join(
    [
        "# SPEC",
        "",
        "## M1: Title (Status: PENDING)",
        "",
        "**Acceptance Criteria:**",
        "",
        "- [ ] the command exits 0",
        "",
        "**Implementation Details:**",
        "",
        "- headingless",
        "",
    ]
)


def run_with(checker, path):
    return subprocess.run([str(checker), str(path)], capture_output=True, text=True)


def write(directory, name, text):
    path = directory / name
    path.write_text(text)
    return path


def milestone(status, criteria):
    return "\n".join(
        [
            f"## M1: Title (Status: {status})",
            "",
            "**Acceptance Criteria:**",
            "",
            criteria,
            "",
        ]
    )


class SpecCheckSemantics:
    """Shared pass/fail cases. Subclasses set `checker` to Python or Scala launcher."""

    checker = CHECK

    def run_checker(self, path):
        return run_with(self.checker, path)

    def test_valid_milestone_exits_zero_with_no_output(self):
        path = write(self.tmp(), "SPEC.ok.md", GOOD_BODY)
        result = self.run_checker(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_heading_that_owns_criteria_must_match_the_status_pattern(self):
        path = write(
            self.tmp(),
            "SPEC.bad-heading.md",
            "\n".join(
                [
                    "## M1: Title",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- x",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:1\n")

    def test_criteria_label_must_be_the_exact_line(self):
        path = write(
            self.tmp(),
            "SPEC.bad-label.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Acceptance criteria:**",
                    "",
                    "- x",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:3\n")

    def test_implementation_details_must_not_be_a_heading(self):
        path = write(
            self.tmp(),
            "SPEC.bad-details.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- x",
                    "",
                    "### Implementation Details",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:7\n")

    def test_nested_milestone_heading_fails(self):
        path = write(
            self.tmp(),
            "SPEC.bad-nested.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- x",
                    "",
                    "### M1a: Child (Status: PENDING)",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:7\n")

    def test_repo_specs_pass(self):
        specs = sorted((ROOT / "docs" / "specs").glob("SPEC.*.md"))
        self.assertGreaterEqual(len(specs), len(SPECS))
        for path in specs:
            with self.subTest(path=path.name):
                result = self.run_checker(path)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")

    def test_repo_specs_directory_passes(self):
        result = self.run_checker(ROOT / "docs" / "specs")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_lesson_bound_hyphen_ids_are_accepted(self):
        for mid in ("M2-implement-1", "M2-implement-1b", "M2-quality-gates-3", "M2a", "M1"):
            with self.subTest(mid=mid):
                path = write(
                    self.tmp(),
                    "SPEC.lesson-id.md",
                    "\n".join(
                        [
                            f"## {mid}: Title (Status: PENDING)",
                            "",
                            "**Acceptance Criteria:**",
                            "",
                            "- [ ] the command exits 0",
                            "",
                        ]
                    ),
                )
                result = self.run_checker(path)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_hyphen_postfix_is_rejected(self):
        path = write(
            self.tmp(),
            "SPEC.bad-hyphen.md",
            "\n".join(
                [
                    "## M2-: Title (Status: PENDING)",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- [ ] the command exits 0",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, f"{path}:1\n")

    def test_details_before_criteria_fails_on_that_line(self):
        path = write(
            self.tmp(),
            "SPEC.details-first.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Implementation Details:**",
                    "",
                    "- later",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- [ ] the command exits 0",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:3\n")

    def test_a_label_with_trailing_text_fails(self):
        for label in ("**Acceptance Criteria:** extra", "**Implementation Details:** extra"):
            with self.subTest(label=label):
                path = write(
                    self.tmp(),
                    "SPEC.trailing.md",
                    "\n".join(
                        [
                            "## M1: Title (Status: PENDING)",
                            "",
                            label,
                            "",
                            "**Acceptance Criteria:**",
                            "",
                            "- [ ] the command exits 0",
                            "",
                        ]
                    ),
                )
                result = self.run_checker(path)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, f"{path}:3\n")

    def test_a_second_label_fails(self):
        path = write(
            self.tmp(),
            "SPEC.second.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- [ ] one",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- [ ] two",
                    "",
                    "**Implementation Details:**",
                    "",
                    "- note",
                    "",
                    "**Implementation Details:**",
                    "",
                    "- again",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"{path}:7\n")

    def test_criteria_then_details_exits_zero(self):
        body = [
            "# SPEC",
            "",
            "## M1: Title (Status: PENDING)",
            "",
            "A short description.",
            "",
            "**Acceptance Criteria:**",
            "",
            "- [ ] the command exits 0",
            "",
        ]
        path = write(self.tmp(), "SPEC.order.md", "\n".join(body))
        result = self.run_checker(path)
        self.assertEqual(result.returncode, 0)
        path.write_text("\n".join(body + ["**Implementation Details:**", "", "- headingless", ""]))
        result = self.run_checker(path)
        self.assertEqual(result.returncode, 0)

    def test_a_plain_bullet_is_not_a_criterion(self):
        path = write(
            self.tmp(),
            "SPEC.plain.md",
            "\n".join(
                [
                    "## M1: Title (Status: PENDING)",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- the command exits 0",
                    "",
                ]
            ),
        )
        result = self.run_checker(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, f"{path}:5\n")

    def test_the_box_matches_the_status(self):
        empty = milestone("PENDING", "- [ ] open")
        checked = milestone("IMPLEMENTED", "- [x] done")
        done = milestone("✅ DONE", "- [x] done")
        mixed = milestone("PARTIALLY_DONE", "- [x] done\n- [ ] open")
        for text in (empty, checked, done, mixed):
            path = write(self.tmp(), "SPEC.box.md", text)
            result = self.run_checker(path)
            self.assertEqual(result.returncode, 0, result.stderr)
        pending_checked = write(self.tmp(), "SPEC.pending-checked.md", milestone("PENDING", "- [x] done"))
        result = self.run_checker(pending_checked)
        self.assertEqual(result.stderr, f"{pending_checked}:5\n")
        implemented_empty = write(
            self.tmp(), "SPEC.implemented-empty.md", milestone("IMPLEMENTED", "- [ ] open")
        )
        result = self.run_checker(implemented_empty)
        self.assertEqual(result.stderr, f"{implemented_empty}:5\n")

    def test_repo_criteria_are_checkboxes(self):
        for path in sorted((ROOT / "docs" / "specs").glob("SPEC.*.md")):
            with self.subTest(path=path.name):
                result = self.run_checker(path)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_wrong_argc_exits_one_quietly(self):
        result = subprocess.run([str(self.checker)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_missing_file_reports_path_line_one(self):
        missing = self.tmp() / "SPEC.no-such.md"
        result = self.run_checker(missing)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, f"{missing}:1\n")

    def test_non_matching_filename_reports_path_line_one(self):
        path = write(self.tmp(), "notes.md", GOOD_BODY)
        result = self.run_checker(path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, f"{path}:1\n")

    def test_directory_reports_each_failing_file(self):
        directory = self.tmp() / "specs"
        directory.mkdir()
        write(directory, "SPEC.good.md", GOOD_BODY)
        bad = write(
            directory,
            "SPEC.bad.md",
            "\n".join(
                [
                    "## M1: Title",
                    "",
                    "**Acceptance Criteria:**",
                    "",
                    "- x",
                    "",
                ]
            ),
        )
        wrong = write(directory, "readme.md", GOOD_BODY)
        result = self.run_checker(directory)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        lines = result.stderr.strip().splitlines()
        self.assertEqual(
            sorted(lines),
            sorted([f"{bad}:1", f"{wrong}:1"]),
        )

    def test_empty_directory_exits_nonzero(self):
        directory = self.tmp() / "empty"
        directory.mkdir()
        result = self.run_checker(directory)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, f"{directory}:1\n")

    def tmp(self):
        return Path(self.enterContext(tempfile.TemporaryDirectory()))


class SpecCheck(SpecCheckSemantics, unittest.TestCase):
    checker = CHECK

    def test_skills_use_the_one_checker(self):
        refine = (ROOT / ".claude" / "skills" / "refine" / "SKILL.md").read_text()
        implement = (ROOT / ".claude" / "skills" / "implement" / "SKILL.md").read_text()
        self.assertIn("Agent proposes → user reviews → agent commits.", refine)
        self.assertIn("Select Milestone", implement)
        for body in (refine, implement):
            self.assertIn("scripts/spec-check", body)
            self.assertNotIn("first_violation", body)
        copies = [p for p in ROOT.rglob("spec-check") if p.is_file()]
        self.assertEqual(copies, [CHECK])

    def test_prose_docs_are_replaced_by_the_specs(self):
        for path in SPECS:
            self.assertTrue(path.is_file(), path)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/specs/SPEC.v1-onion-layering.md", readme)
        self.assertIn("workshop/JOURNEY.md", readme)

    def test_skills_state_the_subsection_order(self):
        sentence = "Headless subsections stay in this order: criteria, then details, each label alone on its line, details never before criteria."
        for name in ("refine", "implement"):
            body = (ROOT / ".claude" / "skills" / name / "SKILL.md").read_text()
            self.assertIn(sentence, body)

    def test_implement_ends_with_how_to_try_it(self):
        body = (ROOT / ".claude" / "skills" / "implement" / "SKILL.md").read_text()
        workflow = body.split("## Important Rules", 1)[0]
        self.assertIn("one block per milestone just implemented", workflow)
        self.assertIn("`v<N>.M<id>`", workflow)

    def test_skills_say_how_a_box_is_written(self):
        refine = (ROOT / ".claude" / "skills" / "refine" / "SKILL.md").read_text()
        implement = (ROOT / ".claude" / "skills" / "implement" / "SKILL.md").read_text()
        self.assertIn("A new criterion is written as `- [ ]`.", refine)
        self.assertIn(
            "Set a criterion's box to `- [x]` only after that criterion's test passes, and leave `- [ ]` otherwise.",
            implement,
        )

    def test_pre_commit_still_uses_python_spec_check(self):
        hook = (ROOT / "hooks" / "pre-commit").read_text()
        self.assertIn('"$root/scripts/spec-check"', hook)
        self.assertNotIn("spec-check-scala", hook)


class SpecCheckScala(SpecCheckSemantics, unittest.TestCase):
    checker = SCALA

    @classmethod
    def setUpClass(cls):
        if not SCALA.is_file():
            raise unittest.SkipTest(f"missing Scala launcher: {SCALA}")


class SpecCheckParkAndQualityGates(unittest.TestCase):
    def test_scala_project_lives_under_scripts_not_skills_2(self):
        self.assertTrue((SCALA_PROJECT / "build.sbt").is_file())
        self.assertTrue((SCALA_PROJECT / "src" / "main" / "scala" / "SpecCheck.scala").is_file())
        self.assertTrue(SCALA.is_file())
        self.assertTrue(os.access(SCALA, os.X_OK))
        self.assertFalse((ROOT / "workshop" / "material" / "skills-2" / "scripts" / "spec-check-scala").exists())

    def test_skills_2_skills_do_not_mention_scala_checker(self):
        refine = (ROOT / "workshop" / "material" / "skills-2" / ".claude" / "skills" / "refine" / "SKILL.md").read_text()
        implement = (
            ROOT / "workshop" / "material" / "skills-2" / ".claude" / "skills" / "implement" / "SKILL.md"
        ).read_text()
        for body in (refine, implement):
            self.assertNotIn("spec-check-scala", body)
            self.assertNotIn("just spec-check", body)

    def test_root_flake_keeps_jdk_sbt_without_new_packages(self):
        flake = (ROOT / "flake.nix").read_text()
        self.assertIn("pkgs.jdk21", flake)
        self.assertIn("pkgs.sbt", flake)
        self.assertNotIn("scala-cli", flake)

    def test_quality_gates_3_material_ships_checker_and_skills(self):
        material = ROOT / "workshop" / "material" / "quality-gates-3"
        self.assertTrue((material / "scripts" / "spec-check-scala" / "run").is_file())
        self.assertTrue((material / "justfile").is_file())
        just = (material / "justfile").read_text()
        self.assertRegex(just, r"(?m)^spec-check")
        refine = (material / ".claude" / "skills" / "refine" / "SKILL.md").read_text()
        implement = (material / ".claude" / "skills" / "implement" / "SKILL.md").read_text()
        for body in (refine, implement):
            self.assertIn("just spec-check", body)
            self.assertNotIn("`scripts/spec-check`", body)

    def test_prepare_delta_includes_quality_gates_3(self):
        justfile = (ROOT / "justfile").read_text()
        self.assertIn("_delta-quality-gates-3:", justfile)
        self.assertIn("quality-gates-3", justfile)


if __name__ == "__main__":
    unittest.main()
