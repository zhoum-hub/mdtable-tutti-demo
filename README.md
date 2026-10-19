# mdtable

A tiny, dependency-free Python Markdown table renderer and parser. This repository is a sample project for a Tutti collaboration demo; the contributors in the demo are fictional personas.

```python
from mdtable import render, parse

table = [["name", "city"], ["Ada", "Berlin"]]
assert parse(render(table)) == table
```

Run the suite with `python3 -m unittest discover -s tests -v`.

The supported format uses a header, a `---` separator row, and single-line string cells. Parsing trims leading and trailing cell whitespace. Multiline cells and non-string values are unsupported.

Cell contents use backslash escapes: `\|` is a literal pipe and `\\` is a literal backslash. Rendering escapes both, so a cell `a\|b` becomes `a\\\|b` and parses back unchanged. In hand-written tables, double every backslash: `| \\\\server\\share |` parses to `\\server\share`.

Version 0.4.2 has a known issue with literal pipe characters in cells. The demo follows a real reproduction, a limited first attempt, a handoff, a second fix, and independent review. Test counts and review findings come from actual execution.
