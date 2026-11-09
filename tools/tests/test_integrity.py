import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("site_tools", Path(__file__).parents[1] / "site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.documents = {"index.html": site.Document('<h1 id="início">Hello</h1>')}
        self.files = {"index.html", "nested/index.html", "images/Tubarão.png", "images/filme Tubarão.png"}

    def test_encoded_spaces_accents_and_relative_paths(self):
        self.assertIsNone(site.resolve_reference("nested/index.html", "../images/filme%20Tubar%C3%A3o.png", self.files, self.documents))

    def test_case_mismatch_fails_on_windows_too(self):
        with self.assertRaisesRegex(ValueError, "case mismatch"):
            site.resolve_reference("index.html", "images/tubarão.png", self.files, self.documents)

    def test_root_relative_url_cannot_escape_project_pages(self):
        with self.assertRaisesRegex(ValueError, "base path"):
            site.resolve_reference("index.html", "/images/Tubarão.png", self.files, self.documents)

    def test_same_origin_absolute_url_is_checked_locally(self):
        with self.assertRaisesRegex(ValueError, "missing local file"):
            site.resolve_reference("index.html", site.BASE + "absent.html", self.files, self.documents)

    def test_internal_anchor_checked_and_percent_decoded(self):
        self.assertIsNone(site.resolve_reference("index.html", "#in%C3%ADcio", self.files, self.documents))
        with self.assertRaisesRegex(ValueError, "missing anchor"):
            site.resolve_reference("index.html", "#missing", self.files, self.documents)

    def test_external_urls_are_returned_for_warning_only_check(self):
        self.assertEqual(site.resolve_reference("index.html", "https://example.org/", self.files, self.documents), "https://example.org/")

    def test_duplicate_ids_and_css_references_are_discovered(self):
        self.assertEqual(site.Document('<p id="a"></p><p id="a"></p>').duplicates, ["a"])
        self.assertEqual(site.css_references('@import "other.css"; a { background: url("img.png"); }'), ["img.png", "other.css"])

    def test_unlinked_pages_are_included_and_tools_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools").mkdir()
            (root / "tools" / "private.html").write_text("private")
            (root / "orphan.html").write_text("public")
            self.assertEqual(site.inventory(root), ["orphan.html"])


if __name__ == "__main__":
    unittest.main()
