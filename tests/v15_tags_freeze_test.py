"""outer.v15.M3a-M3d, M5c — the frozen tag list must agree with the live tags."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAGS_FILE = ROOT / "app" / "snapshots" / "TAGS"
CHAIN = ["app-v1", "app-v2", "app-v3", "app-v4", "app-v4-quiet"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def frozen():
    pairs = {}
    for line in TAGS_FILE.read_text(encoding="utf-8").splitlines():
        name, sha = line.split()
        pairs[name] = sha
    return pairs


class TagsFreeze(unittest.TestCase):
    def test_every_tag_in_the_chain_is_frozen_with_a_real_sha(self):
        pairs = frozen()
        self.assertEqual(list(pairs), CHAIN)
        for name, sha in pairs.items():
            self.assertRegex(sha, r"^[0-9a-f]{40}$", f"{name} is still a placeholder")

    def test_frozen_sha_equals_the_commit_the_live_tag_points_at(self):
        live = git("tag", "-l", "app-v*").stdout.split()
        if not live:
            self.skipTest("no live tags in this clone; the freeze file is the record")
        for name, sha in frozen().items():
            if name not in live:
                continue
            self.assertEqual(git("rev-parse", f"{name}^{{commit}}").stdout.strip(), sha, name)

    def test_the_frozen_commits_form_one_ancestry_chain(self):
        pairs = frozen()
        if git("cat-file", "-e", f"{pairs['app-v1']}^{{commit}}").returncode != 0:
            self.skipTest("frozen commits are not in this clone")
        for older, newer in zip(CHAIN, CHAIN[1:]):
            r = git("merge-base", "--is-ancestor", pairs[older], pairs[newer])
            self.assertEqual(r.returncode, 0, f"{older} is not an ancestor of {newer}")


if __name__ == "__main__":
    unittest.main()
