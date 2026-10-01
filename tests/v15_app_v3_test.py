"""outer.v15.M3c — app-v3 config + tag + tree."""
import subprocess, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
class AppV3(unittest.TestCase):
    def test_v3_and_tree(self):
        v3 = (APP / "docs/specs/SPEC.v3-todo-list-cli-config.md").read_text()
        self.assertNotIn("(Status: PENDING)", v3)
        self.assertIn("0.17.8", v3)
        self.assertTrue((APP / "snapshots/app-v3.TREE").is_file())
    def test_tag_or_freeze(self):
        tags = subprocess.run(["git","tag","-l","app-v3"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        if tags != "app-v3":
            self.assertIn("app-v3", (APP/"snapshots/TAGS").read_text())
    def test_config_suite(self):
        self.assertTrue((APP/"src/test/scala/todo/config/AppConfigSuite.scala").is_file())
if __name__ == "__main__":
    unittest.main()
