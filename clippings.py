#!/usr/bin/env python
"""
Converts Kindle clippings ('My Clippings.txt') into JSON, CSV, or Markdown.
"""
from re import Match, Pattern, compile, match

# Clippings are separated by this string.
CLIPPINGS_DELIMITER: str = "==========\n"

# Epub books and such have titles of the form `$title ($author)`.
EPUB_TITLE_RE: Pattern[str] = compile(r"^(.+) \((.*)\)$")
# Calibre PDFs have titles of the form `$title - $author`.
PDF_TITLE_RE: Pattern[str] = compile(r"^(.+) - (.*)$")


def parse_title(title_line: str) -> str:
    # Try parsing an EPUB-style title.
    matches: Match[str] = match(EPUB_TITLE_RE, title_line)
    if matches:
        return matches.group(1).strip()
    # Try parsing a Calibre-style title.
    matches = match(PDF_TITLE_RE, title_line)
    if matches:
        title: str = matches.group(1).replace("_ ", ": ").strip()
        if title.endswith(", The"):
            return "The " + title.replace(", The", "")
        else:
            return title
    # On failure, return the title line unchanged.
    return title_line.strip()
