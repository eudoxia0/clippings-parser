#!/usr/bin/env python
"""
Converts Kindle clippings ('My Clippings.txt') into JSON, CSV, or Markdown.
"""
from re import Pattern, compile

# Clippings are separated by this string.
CLIPPINGS_DELIMITER: str = "==========\n"

# Epub books and such have titles of the form `$title ($author)`.
EPUB_TITLE_RE: Pattern[str] = compile(r"^(.+) \((.*)\)$")
# Calibre PDFs have titles of the form `$title - $author`.
PDF_TITLE_RE: Pattern[str] = compile(r"^(.+) - (.*)$")
