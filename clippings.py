#!/usr/bin/env python
"""
Converts Kindle clippings ('My Clippings.txt') into JSON, CSV, or Markdown.
"""
import argparse
import csv
import json
import sys
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
    # Every clipping is of the form: title \n location \n\n text. So assert
    # that there are more than three lines.
    assert len(lines) > 3
    assert lines[2] == ""
    # Extract the important stuff.
    title_line: str = lines[0]
    # source_line: str = lines[1]
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


def filter_by_title(
    clippings: list[dict], title_filter: str | None
) -> list[dict]:
    return [c for c in clippings if filter_pred(c, title_filter)]


#
# JSON
#


def dump_json(clippings: list[dict]):
    print(json.dumps(clippings, indent=True))


#
# CSV
#


def dump_csv(clippings: list[dict]):
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["author", "title", "text"],
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()
    for row in clippings:
        writer.writerow(row)


#
# Markdown
#


def remove_duplicates(lst: list[str]) -> list[str]:
    seen: set[str] = set()
    res: list[str] = []
    for elem in lst:
        if not (elem in seen):
            seen.add(elem)
            res.append(elem)
    return res


def dump_markdown(clippings: list[dict]):
    # Nothing to do.
    if len(clippings) == 0:
        return
    # Group by title.
    all_titles: list[str] = remove_duplicates(c["title"] for c in clippings)
    for title in all_titles:
        print(f"# {title}")
        filtered: list[dict] = filter_by_title(clippings, title)
        first: bool = True
        for clip in filtered:
            if first:
                first = False
            else:
                print("---")
            print()
            text: str = clip["text"]
            assert len(title) > 0
            print(text)
            print()


#
# Entrypoint
#


def main(output_format: str, title_filter: str | None):
    # Read the entire stdin as a string.
    contents: str = sys.stdin.read()
    # The clippings are CRLF, so trim that.
    contents = contents.replace("\r", "")
    # Split by delimiter.
    blocks: list[str] = contents.split(CLIPPINGS_DELIMITER)
    # Trim any empty blocks, typically this will be the last item in the list.
    blocks = [b for b in blocks if b.strip() != ""]
    # Parse each clipping.
    clippings: list[dict] = [parse_clipping(b) for b in blocks]
    # Sort.
    clippings = sorted(
        clippings, key=lambda d: (d["author"] or "") + ":" + d["title"]
    )
    # Filter by title.
    clippings = filter_by_title(clippings, title_filter)
    # Dispatch on the output format.
    dispatch = {
        "json": dump_json,
        "csv": dump_csv,
        "md": dump_markdown,
    }
    dispatch[output_format](clippings)


if __name__ == "__main__":
    # Parse CLI arguments.
    parser = argparse.ArgumentParser(
        prog="clippings",
        description="Turns Kindle clippings into JSON, CSV, or Markdown.",
    )
    parser.add_argument(
        "--format",
        help="The output format.",
        choices=["json", "csv", "md"],
        default="json",
    )
    parser.add_argument(
        "--title", help="Filter only clippings with the given title."
    )
    args = parser.parse_args()
    main(args.format, args.title)
