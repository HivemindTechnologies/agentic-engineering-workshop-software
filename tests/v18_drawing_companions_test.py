"""outer.v18 — drawing companions: contract, checksum, generate-missing, skill."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "drawing-companions"
SKILL = ROOT / ".claude" / "skills" / "drawing-companions" / "SKILL.md"
JUST = ROOT / "justfile"
DRAWINGS = ROOT / "docs" / "drawings"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def write_drawing(directory: Path, stem: str, payload: bytes) -> Path:
    path = directory / f"{stem}.excalidraw"
    path.write_bytes(payload)
    return path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DrawingCompanionsM1(unittest.TestCase):
    def test_companion_path_is_same_stem_md_beside_drawing(self):
        import runpy

        mod = runpy.run_path(str(SCRIPT))
        drawing = Path("/tmp/docs/drawings/hard-easy.excalidraw")
        self.assertEqual(
            mod["companion_path_for"](drawing),
            Path("/tmp/docs/drawings/hard-easy.md"),
        )

    def test_matching_checksum_is_not_stale_mismatch_is_stale(self):
        import runpy

        mod = runpy.run_path(str(SCRIPT))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b'{"type":"excalidraw","elements":[]}\n'
            drawing = write_drawing(root, "demo", payload)
            digest = sha256(payload)
            text = mod["render_companion"](drawing, checksum=digest)
            companion = mod["parse_companion"](text)
            self.assertFalse(mod["is_stale"](drawing, companion))
            companion.source_sha256 = "0" * 64
            self.assertTrue(mod["is_stale"](drawing, companion))

    def test_wrong_stem_pairing_fails_contract(self):
        import runpy

        mod = runpy.run_path(str(SCRIPT))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            drawing = write_drawing(root, "alpha", b"alpha\n")
            wrong = root / "beta.md"
            wrong.write_text(
                mod["render_companion"](drawing).replace(
                    "drawing: alpha.excalidraw", "drawing: beta.excalidraw"
                ),
                encoding="utf-8",
            )
            # Path itself is wrong stem.
            errors = mod["contract_errors"](drawing, wrong)
            self.assertTrue(errors)
            self.assertTrue(any("beside" in e or "must be" in e for e in errors))


class DrawingCompanionsM2(unittest.TestCase):
    def test_generate_missing_creates_stub_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_drawing(root, "one", b"one-bytes\n")
            write_drawing(root, "two", b"two-bytes\n")
            existing = root / "two.md"
            existing.write_text(
                textwrap.dedent(
                    """\
                    ---
                    drawing: two.excalidraw
                    source_sha256: deadbeef
                    generated_by: hand
                    generated_at: 2000-01-01T00:00:00Z
                    ---

                    <!-- generated:begin -->
                    ## Summary

                    Keep me.
                    <!-- generated:end -->

                    <!-- curated:begin -->
                    ## Ideas

                    Human note.
                    <!-- curated:end -->
                    """
                ),
                encoding="utf-8",
            )
            before = existing.read_text(encoding="utf-8")
            result = run("generate-missing", str(root))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            one_md = root / "one.md"
            self.assertTrue(one_md.is_file())
            body = one_md.read_text(encoding="utf-8")
            self.assertIn("source_sha256:", body)
            self.assertIn("<!-- generated:begin -->", body)
            self.assertIn("<!-- curated:begin -->", body)
            self.assertIn("_Stub", body)
            self.assertEqual(existing.read_text(encoding="utf-8"), before)

    def test_status_lists_missing_and_stale_fail_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_drawing(root, "fresh", b"fresh\n")
            write_drawing(root, "gone", b"gone\n")
            # missing companion for fresh; stale for gone
            digest = sha256(b"old-gone\n")
            (root / "gone.md").write_text(
                textwrap.dedent(
                    f"""\
                    ---
                    drawing: gone.excalidraw
                    source_sha256: {digest}
                    generated_by: drawing-companions
                    generated_at: 2000-01-01T00:00:00Z
                    ---

                    <!-- generated:begin -->
                    ## Summary

                    old
                    <!-- generated:end -->

                    <!-- curated:begin -->
                    ## Ideas

                    note
                    <!-- curated:end -->
                    """
                ),
                encoding="utf-8",
            )
            board = run("status", str(root))
            self.assertEqual(board.returncode, 0, board.stderr)
            self.assertIn("missing  fresh.excalidraw", board.stdout)
            self.assertIn("stale    gone.excalidraw", board.stdout)
            failing = run("status", "--fail", str(root))
            self.assertEqual(failing.returncode, 1)

    def test_just_recipes_expose_generate_and_status(self):
        just = JUST.read_text(encoding="utf-8")
        self.assertRegex(just, r"(?m)^drawing-companions-generate\b")
        self.assertRegex(just, r"(?m)^drawing-companions-status\b")
        self.assertRegex(just, r"(?m)^drawing-companions-check\b")
        for recipe in (
            "drawing-companions-generate",
            "drawing-companions-status",
            "drawing-companions-check",
        ):
            shown = subprocess.run(
                ["just", "--show", recipe],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertIn("drawing-companions", shown.stdout)


class DrawingCompanionsM3(unittest.TestCase):
    def test_skill_documents_interpret_reinterpret_and_contract(self):
        self.assertTrue(SKILL.is_file())
        text = SKILL.read_text(encoding="utf-8")
        lowered = text.lower()
        for needle in (
            "excalidraw",
            "companion",
            "interpret",
            "reinterpret",
            "what does this drawing show",
            "checksum",
            "curated",
            "preserve",
            "ideas",
            "docs/drawings",
            "source_sha256",
            "drawing-companions",
        ):
            self.assertIn(needle, lowered, needle)
        self.assertIn("<!-- generated:begin -->", text)
        self.assertIn("<!-- curated:begin -->", text)
        self.assertIn("generate-missing", text)
        self.assertIn("stale", lowered)


if __name__ == "__main__":
    unittest.main()
