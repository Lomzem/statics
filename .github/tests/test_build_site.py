"""Exercise the site builder through its command-line interface and output files."""

from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


BUILDER = Path(__file__).resolve().parents[1] / "scripts/build_site.py"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.parents = []
        self.label = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append([dict(attrs)["href"], "", self.parents[-2:]])
            self.label = self.links[-1]
        self.parents.append(tag)

    def handle_endtag(self, tag):
        if tag == "a":
            self.label = None
        if tag in self.parents:
            del self.parents[self.parents.index(tag):]

    def handle_data(self, data):
        if self.label is not None:
            self.label[1] += data


class BuildSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)
        self.output = self.source / "_site"

    def write(self, path, content):
        target = self.source / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def build(self):
        subprocess.run(
            [sys.executable, str(BUILDER), str(self.source), str(self.output)],
            check=True, capture_output=True, text=True,
        )
        links = Links()
        links.feed((self.output / "index.html").read_text(encoding="utf-8"))
        return links.links

    def test_catalogue_links_to_visible_pages_in_path_order_and_preserves_assets(self):
        self.write("z.html", "<title> First alphabetically </title>")
        self.write("index.html", "<title>Old landing page</title>")
        self.write("nested/index.html", "<TITLE> Nested\n page </TITLE>")
        self.write("no-title.html", "<p>No title</p>")
        self.write("empty-title.html", "<title> \n </title>")
        self.write("a space #?&é.html", "<title>Fish &amp; &lt;chips&gt;</title>")
        self.write(".hidden/secret.html", "<title>Hidden</title>")
        self.write("nested/.hidden/secret.html", "<title>Hidden</title>")
        self.write("nested/style.css", "body { color: navy; }")
        self.assertEqual(self.build(), [
            ["a%20space%20%23%3F%26%C3%A9.html", "Fish & <chips>", ["ul", "li"]],
            ["empty-title.html", "empty-title.html", ["ul", "li"]],
            ["nested/index.html", "Nested page", ["ul", "li"]],
            ["no-title.html", "no-title.html", ["ul", "li"]],
            ["z.html", "First alphabetically", ["ul", "li"]],
        ])
        self.assertEqual(
            (self.output / "nested/style.css").read_text(), "body { color: navy; }"
        )
        self.assertEqual(
            (self.output / "nested/index.html").read_text(),
            "<TITLE> Nested\n page </TITLE>",
        )
        self.assertFalse((self.output / ".hidden").exists())
        self.assertFalse((self.output / "nested/.hidden").exists())

    def test_rebuild_reflects_renames_and_removals_without_indexing_its_output(self):
        self.write("old.html", "<title>Old</title>")
        self.write("removed.html", "<title>Removed</title>")
        self.write("old.css", "old styles")
        self.build()
        (self.source / "old.html").rename(self.source / "new.html")
        (self.source / "removed.html").unlink()
        (self.source / "old.css").unlink()
        self.write("new.html", "<title>New</title>")
        expected = [["new.html", "New", ["ul", "li"]]]
        self.assertEqual(self.build(), expected)
        self.assertFalse((self.output / "old.html").exists())
        self.assertFalse((self.output / "removed.html").exists())
        self.assertFalse((self.output / "old.css").exists())
        self.assertFalse((self.output / "_site").exists())
        self.assertEqual(self.build(), expected)


if __name__ == "__main__":
    unittest.main()
