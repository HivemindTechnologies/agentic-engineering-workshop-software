import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".claude" / "agents" / "instructor.md"


class InstructorAgent(unittest.TestCase):
    def test_frontmatter_and_principles(self):
        text = AGENT.read_text()
        self.assertIn("name: instructor\n", text)
        self.assertIn("description:", text)
        self.assertIn("permissionMode: acceptEdits\n", text)
        self.assertNotIn("maxTurns", text)
        body = text.split("---", 2)[2]
        self.assertIn("workshop/JOURNEY.md", body)
        self.assertIn("table of contents", body)
        self.assertIn("their order", body)
        self.assertIn("their headlines", body)
        self.assertIn("their content", body)
        self.assertIn("keeps that table intact", body)
        self.assertIn("state that correction explicitly", body)
        self.assertIn("follow-up questions", body)
        self.assertIn("expected observations", body)
        self.assertIn("plain refine prompt", body)
        self.assertIn("/refine", body)
        self.assertIn("settled choices", body)
        self.assertIn("toward implementation", body)
        self.assertIn("One short prompt per lesson", body)
        self.assertIn("new segment", body)
        self.assertIn("stuck participant", body)
        self.assertIn("verdict: pass", body)
        self.assertIn("M1 similarities are evidence", body)
        self.assertIn("not a pass or a fail", body)
        self.assertNotIn("develop/", text)
        self.assertNotIn("verdict: fail", text)
        self.assertNotIn("write verdict: pass", body)
        self.assertIn("do not do the participant's work", body)
        self.assertIn("JUDGE.md", body)
        self.assertIn("not yet judged", body)
        self.assertIn("support that lesson and name it", body)
        self.assertIn("Do not add a fact to a later lesson", body)
        self.assertIn("already smooth", body)
        self.assertIn("one *PROMPT TO TEST* block", body)
        self.assertIn("outside that block", body)
        self.assertIn("not a second prompt", body)
        self.assertIn("your judgment", body)
        self.assertIn("similarity to the previous prompt and to the next prompt", body)
        self.assertIn("workshop/prompt-distance.txt", body)
        self.assertIn("do not write a last: mark that the status line does not show", body)

    def test_harness_does_not_copy_the_instructor_into_the_sandbox(self):
        justfile = (ROOT / "justfile").read_text()
        session = (ROOT / "scripts" / "participant-session").read_text()
        forks = (ROOT / "scripts" / "lesson-forks").read_text()
        self.assertNotIn("instructor.md", justfile)
        self.assertNotIn("instructor.md", session)
        self.assertNotIn("instructor.md", forks)
        self.assertIn(".claude/agents/participant.md", justfile)


if __name__ == "__main__":
    unittest.main()
