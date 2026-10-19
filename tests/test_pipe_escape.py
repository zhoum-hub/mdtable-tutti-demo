"""Regression tests for literal pipe characters in cells (issue #1).

These tests are intentionally failing on the 0.4.2 baseline. They describe the
behavior a fix must provide: a literal ``|`` inside a cell, and a literal
backslash that precedes one, survive a render/parse round trip without changing
the table's structure.
"""

import unittest

from mdtable import parse, render


PIPE_ROUNDTRIPS = [
    # Minimal reproduction from the issue.
    [["cmd", "desc"], ["a | b", "pipe in a shell command"]],
    # A pipe is the only content of the cell.
    [["|"]],
    # Pipes at both cell edges and repetitions in the middle.
    [["|a|"]],
    [["a|"]],
    [["|a"]],
    [["a|b|c"]],
    # Pipe in a header cell.
    [["h|1", "h2"], ["v1", "v2"]],
    # Pipe in several columns and next to an empty cell.
    [["a|b", "c|d"], ["", "|"]],
    # Pipe surrounded by internal whitespace must keep that whitespace.
    [["a | b"]],
    # A literal backslash directly before a pipe, and next to one.
    [["a\\|b"]],
    [["a\\\\|b"]],
    [["a|\\b"]],
    [["a|b\\"]],
    # Backslashes without a pipe keep working (guards the escape design).
    [["a\\b", "c|d"]],
]


class PipeEscapeTests(unittest.TestCase):
    def test_issue_example_roundtrip(self):
        rows = [["cmd", "desc"], ["a | b", "pipe in a shell command"]]
        self.assertEqual(parse(render(rows)), rows)

    def test_pipe_does_not_add_columns(self):
        rows = [["h"], ["a|b"]]
        parsed = parse(render(rows))
        self.assertEqual(len(parsed), 2)
        self.assertEqual(len(parsed[0]), 1)
        self.assertEqual(len(parsed[1]), 1)

    def test_pipe_roundtrips(self):
        for rows in PIPE_ROUNDTRIPS:
            with self.subTest(rows=rows):
                self.assertEqual(parse(render(rows)), rows)


# --- Coverage derived from the independent review probes --------------------

# The review checked every run length from zero through 64.
MAX_BACKSLASH_RUN = 64


def hand_written_row(backslashes, tail):
    """Raw row text with ``backslashes`` escaped backslashes before ``tail``."""
    return "| " + "\\" * backslashes + tail


class BackslashRunTests(unittest.TestCase):
    """Zero through 64 backslashes immediately before a pipe."""

    def test_rendered_runs_roundtrip(self):
        for count in range(MAX_BACKSLASH_RUN + 1):
            run = "\\" * count
            cells = [run + "|", "|" + run, "a" + run + "|b", run + "|" + run]
            for cell in cells:
                with self.subTest(backslashes=count, cell=cell):
                    rows = [["h", "other"], [cell, "value"]]
                    self.assertEqual(parse(render(rows)), rows)

    def test_handwritten_odd_run_escapes_pipe(self):
        # 2k+1 backslashes before a pipe decode to k backslashes and a literal
        # pipe; the cell keeps its column.
        for count in range(1, MAX_BACKSLASH_RUN + 1, 2):
            with self.subTest(backslashes=count):
                text = "| h |\n| --- |\n" + hand_written_row(count, "|x |")
                expected = [["h"], ["\\" * (count // 2) + "|x"]]
                self.assertEqual(parse(text), expected)

    def test_handwritten_even_run_ends_cell(self):
        # 2k backslashes before a pipe decode to k backslashes and a column
        # delimiter.
        for count in range(0, MAX_BACKSLASH_RUN + 1, 2):
            with self.subTest(backslashes=count):
                text = "| h1 | h2 |\n| --- | --- |\n" + hand_written_row(count, "|x |")
                expected = [["h1", "h2"], ["\\" * (count // 2), "x"]]
                self.assertEqual(parse(text), expected)

    def test_handwritten_odd_run_keeps_columns(self):
        # In a two-column row the escaped pipe must not become a delimiter;
        # the later, unescaped pipe still splits the cells.
        for count in range(1, MAX_BACKSLASH_RUN + 1, 2):
            with self.subTest(backslashes=count):
                text = "| h1 | h2 |\n| --- | --- |\n" + hand_written_row(
                    count, "|x | y |"
                )
                expected = [["h1", "h2"], ["\\" * (count // 2) + "|x", "y"]]
                self.assertEqual(parse(text), expected)


class WindowsPathTests(unittest.TestCase):
    WINDOWS_PATHS = [
        "C:\\temp\\",
        "C:\\Users\\Maya",
        "C:\\Users\\Maya\\",
        "\\\\server\\share",
        "\\\\server\\share\\",
        "C:\\",
        "\\",
        "\\\\",
        "C:\\temp\\file.txt",
        "D:\\a|b\\",
    ]

    def test_rendered_paths_roundtrip(self):
        for path in self.WINDOWS_PATHS:
            with self.subTest(path=path):
                rows = [["path"], [path]]
                self.assertEqual(parse(render(rows)), rows)
        # A trailing path next to a cell containing a pipe.
        rows = [["C:\\x|y\\", "C:\\temp\\"]]
        self.assertEqual(parse(render(rows)), rows)

    def test_handwritten_trailing_paths(self):
        cases = [
            # Padded and unpadded trailing backslashes before the final border.
            ("| C:\\\\temp\\\\ |\n| --- |", "C:\\temp\\"),
            ("| C:\\\\temp\\\\|\n| --- |", "C:\\temp\\"),
            ("| a\\\\ |\n| --- |", "a\\"),
            ("| a\\\\|\n| --- |", "a\\"),
            ("| a\\ |\n| --- |", "a\\"),
            # UNC path: every backslash is doubled in the raw text.
            ("| \\\\\\\\server\\\\share\\\\ |\n| --- |", "\\\\server\\share\\"),
            # Escaped pipe between trailing backslashes.
            ("| D:\\\\a\\|b\\\\ |\n| --- |", "D:\\a|b\\"),
        ]
        for text, path in cases:
            with self.subTest(text=text):
                self.assertEqual(parse(text), [[path]])


class UnknownEscapeTests(unittest.TestCase):
    def test_unknown_escapes_stay_literal(self):
        for cell in ["a\\q", "\\z", "\\?", "\\_", "a\\q\\z", "C:\\temp\\q"]:
            with self.subTest(cell=cell):
                self.assertEqual(parse("| " + cell + " |\n| --- |"), [[cell]])

    def test_unknown_escape_does_not_escape_pipe(self):
        text = "| h1 | h2 |\n| --- | --- |\n| a\\q|b |"
        self.assertEqual(parse(text), [["h1", "h2"], ["a\\q", "b"]])


class MalformedEscapedRowTests(unittest.TestCase):
    def test_malformed_escaped_rows_rejected(self):
        cases = [
            # Escaped pipe leaves one header cell for a two-column separator.
            "| a\\|b |\n| --- | --- |",
            # Escaped pipe leaves one body cell in a two-column row.
            "| h1 | h2 |\n| --- | --- |\n| a\\|b |",
            # An even run splits a one-column body row into two cells.
            "| h |\n| --- |\n| a\\\\|b |",
            # An escaped pipe inside the separator is not the --- marker.
            "| h1 | h2 |\n| --- \\| --- |",
        ]
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse(text)


class DeterministicRoundtripTests(unittest.TestCase):
    """A small fixed cross-section of pipes, backslashes, and paths."""

    CASES = [
        [[""]],
        [["|"]],
        [["\\"]],
        [["\\|"]],
        [["|\\"]],
        [["\\\\|"]],
        [["C:\\temp\\"]],
        [["\\\\server\\share\\"]],
        [["a\\|b"]],
        [["a\\\\|b"]],
        [["a|\\b"]],
        [["a|b\\"]],
        [["|a|", "\\b\\"]],
        [["h|1", "h2\\"], ["", "|"]],
        [["C:\\x|y\\", "C:\\temp\\"]],
        [["a | b", "c\\|d"]],
        [["x"], ["a|b"], ["C:\\temp\\"], ["|"]],
    ]

    def test_deterministic_roundtrips(self):
        for rows in self.CASES:
            with self.subTest(rows=rows):
                self.assertEqual(parse(render(rows)), rows)


if __name__ == "__main__":
    unittest.main()
