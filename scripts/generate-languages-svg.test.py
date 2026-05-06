"""Tests for generate-languages-svg.py."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "generate-languages-svg.py"


class GenerateLanguagesSVGTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, page1, page2=None, check=True):
        env = {**os.environ, "PAGE1_JSON": str(page1)}
        if page2 is not None:
            env["PAGE2_JSON"] = str(page2)
        return subprocess.run(
            ["python3", str(SCRIPT)],
            cwd=self.cwd,
            env=env,
            capture_output=True,
            text=True,
            check=check,
        )

    @staticmethod
    def _page(edges):
        return {
            "data": {
                "viewer": {
                    "repositories": {"nodes": [{"languages": {"edges": edges}}]}
                }
            }
        }

    def _write_page(self, path, edges):
        path.write_text(json.dumps(self._page(edges)))

    def test_writes_svg_with_single_page(self):
        page1 = self.cwd / "p1.json"
        self._write_page(page1, [{"size": 1000, "node": {"name": "TypeScript"}}])
        self._run(page1)
        out = (self.cwd / "github-languages.svg").read_text()
        self.assertIn("<svg", out)
        self.assertIn("TypeScript", out)
        self.assertIn("100.0%", out)

    def test_excludes_html_and_css(self):
        page1 = self.cwd / "p1.json"
        self._write_page(
            page1,
            [
                {"size": 500, "node": {"name": "HTML"}},
                {"size": 500, "node": {"name": "CSS"}},
                {"size": 1000, "node": {"name": "Python"}},
            ],
        )
        self._run(page1)
        out = (self.cwd / "github-languages.svg").read_text()
        self.assertNotIn(">HTML<", out)
        self.assertNotIn(">CSS<", out)
        self.assertIn("Python", out)

    def test_combines_two_pages(self):
        page1 = self.cwd / "p1.json"
        page2 = self.cwd / "p2.json"
        self._write_page(page1, [{"size": 100, "node": {"name": "Go"}}])
        self._write_page(page2, [{"size": 300, "node": {"name": "Go"}}])
        self._run(page1, page2)
        out = (self.cwd / "github-languages.svg").read_text()
        self.assertIn("Go", out)
        self.assertIn("100.0%", out)

    def test_missing_page2_is_optional(self):
        page1 = self.cwd / "p1.json"
        self._write_page(page1, [{"size": 1, "node": {"name": "Rust"}}])
        bogus = self.cwd / "does-not-exist.json"
        self._run(page1, bogus)
        self.assertTrue((self.cwd / "github-languages.svg").exists())

    def test_top_8_languages_only(self):
        edges = [
            {"size": 100 - i, "node": {"name": f"Lang{i}"}} for i in range(15)
        ]
        page1 = self.cwd / "p1.json"
        self._write_page(page1, edges)
        self._run(page1)
        out = (self.cwd / "github-languages.svg").read_text()
        for i in range(8):
            self.assertIn(f"Lang{i} ", out)
        self.assertNotIn("Lang8 ", out)

    def test_missing_page1_returns_nonzero(self):
        page1 = self.cwd / "does-not-exist.json"
        result = self._run(page1, check=False)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
