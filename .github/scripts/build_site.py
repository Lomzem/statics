"""Copy static content and generate a link catalogue. Uses only Python's stdlib."""

import argparse
from html import escape
from html.parser import HTMLParser
import os
from pathlib import Path
import shutil
from urllib.parse import quote


class PageTitle(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def page_title(path):
    parser = PageTitle()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join("".join(parser.parts).split())


def build(source, output):
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    pages = []
    for directory, directories, files in os.walk(source):
        directory = Path(directory)
        directories[:] = [
            name for name in directories
            if not name.startswith(".") and directory / name != output
        ]
        for name in files:
            path = directory / name
            relative = path.relative_to(source)
            if relative == Path("index.html"):
                continue
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            if path.suffix == ".html":
                pages.append((relative.as_posix(), page_title(path)))

    links = "\n".join(
        f'    <li><a href="{escape(quote(path), quote=True)}">'
        f'{escape(title or path)}</a></li>'
        for path, title in sorted(pages)
    )
    (output / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '  <title>Statics</title>\n'
        '  <link rel="stylesheet" href="assets/index.css">\n'
        '</head>\n<body>\n<main>\n'
        '  <h1>Statics</h1>\n  <ul role="list">\n'
        f'{links}\n  </ul>\n</main>\n</body>\n</html>\n',
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if not source.is_dir():
        parser.error("source must be a directory")
    if output == source or output in source.parents:
        parser.error("output must not be the source directory or its ancestor")
    build(source, output)


if __name__ == "__main__":
    main()
