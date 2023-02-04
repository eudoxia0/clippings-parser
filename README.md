`clippings.py` is a script to export your Kindle clippings to JSON, CSV, or Markdown.

# Usage

Default output is JSON:

```bash
cat 'My Clippings.txt' | ./clippings.py
```

You can pass `--format=csv` or `--format=md` to get CSV or Markdown output:

```bash
cat highlights.txt | ./clippings.py --format=csv
cat highlights.txt | ./clippings.py --format=md
```

The Markdown output is useful for quick insertion into a personal wiki like [Obsidian](https://obsidian.md/).

All three outputs support the `--title` flag, which filters for any work with the given title:

```
cat highlights.txt | ./clippings.py --format=csv --title="The Diamond Age"
```


# License

Copyright 2023 [Fernando Borretti](https://borretti.me/)

Released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).