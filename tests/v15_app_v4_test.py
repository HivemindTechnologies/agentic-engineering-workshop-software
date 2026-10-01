"""outer.v15.M3d — app-v4 planning fields + tag + notes."""
import subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
class AppV4(unittest.TestCase):
    def test_v4_tree_notes(self):
        v4 = (APP/"docs/specs/SPEC.v4-todo-list-cli-planning.md").read_text()
        self.assertNotIn("(Status: PENDING)", v4)
        self.assertTrue((APP/"snapshots/app-v4.TREE").is_file())
        notes = (APP/"snapshots/ABSTRACTION_NOTES.md").read_text()
        self.assertIn("AppConfig.resolve", notes)
    def test_tag_or_freeze(self):
        tags = subprocess.run(["git","tag","-l","app-v4"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        if tags != "app-v4":
            self.assertIn("app-v4", (APP/"snapshots/TAGS").read_text())
    def test_domain_features(self):
        todos = (APP/"src/main/scala/todo/core/Todos.scala").read_text()
        self.assertIn("due", todos.lower())
        self.assertIn("filter", todos)
if __name__ == "__main__":
    unittest.main()
