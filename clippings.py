#!/usr/bin/env python
"""
Converts Kindle clippings ('My Clippings.txt') into JSON, CSV, or Markdown.
"""
from re import Match, Pattern, compile, match

#
# Parsing
#

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


def parse_author(title_line: str) -> str | None:
    # Try parsing an EPUB-style title.
    matches: Match[str] = match(EPUB_TITLE_RE, title_line)
    if matches:
        return matches.group(2).strip()
    # Try parsing a Calibre-style title.
    matches = match(PDF_TITLE_RE, title_line)
    if matches:
        return matches.group(2).strip()
    # On failure, return `None`.
    return None


def parse_clipping(block: str) -> dict:
    # Split the block into lines.
    lines: list[str] = block.split("\n")
    # Every clipping is of the form: title \n location \n\n text. So assert that there are
    # more than three lines.
    assert len(lines) > 3
    assert lines[2] == ""
    # Extract the important stuff.
    title_line: str = lines[0]
    source_line: str = lines[1]
    text_block: list[str] = [line for line in lines[3:] if line.strip() != ""]
    # Parse the title and author.
    title: str = parse_title(title_line)
    author: str | None = parse_author(title_line)
    # Construct a JSON object.
    return {"title": title, "author": author, "text": "\n".join(text_block)}


#
# Filtering
#


def filter_pred(c: dict, title_filter: str | None) -> bool:
    if title_filter is None:
        return True
    else:
        return c["title"] == title_filter


def filter_by_title(clippings: list[dict], title_filter: str | None) -> list[dict]:
    return [c for c in clippings if filter_pred(c, title_filter)]
