import unittest

from mdtable import parse, render


class BaselineTests(unittest.TestCase):
    def test_empty_render(self):
        self.assertEqual(render([]), "")

    def test_empty_parse(self):
        self.assertEqual(parse(""), [])

    def test_blank_parse(self):
        self.assertEqual(parse(" \n "), [])

    def test_header_only(self):
        self.assertEqual(render([["name"]]), "| name |\n| --- |")

    def test_render_two_columns(self):
        self.assertEqual(render([["a", "b"], ["1", "2"]]), "| a | b |\n| --- | --- |\n| 1 | 2 |")

    def test_ragged_rejected(self):
        with self.assertRaises(ValueError):
            render([["a"], ["b", "c"]])

    def test_no_columns_rejected(self):
        with self.assertRaises(ValueError):
            render([[]])

    def test_number_rejected(self):
        with self.assertRaises(TypeError):
            render([[1]])

    def test_newline_rejected(self):
        with self.assertRaises(ValueError):
            render([["a\nb"]])

    def test_carriage_return_rejected(self):
        with self.assertRaises(ValueError):
            render([["a\rb"]])

    def test_missing_separator_rejected(self):
        with self.assertRaises(ValueError):
            parse("| a |")

    def test_bad_separator_rejected(self):
        with self.assertRaises(ValueError):
            parse("| a |\n| xyz |")

    def test_missing_border_rejected(self):
        with self.assertRaises(ValueError):
            parse("a\n| --- |")

    def test_wrong_width_rejected(self):
        with self.assertRaises(ValueError):
            parse("| a |\n| --- |\n| b | c |")


ROUNDTRIPS = [
    [["name"]],
    [["name"], ["Ada"]],
    [["a", "b"], ["one", "two"]],
    [["x", "y", "z"], ["1", "2", "3"]],
    [["empty"], [""]],
    [["unicode"], ["café"]],
    [["emoji"], ["🌍"]],
    [["path"], ["C:\\temp\\"]],
    [["path"], ["C:\\Users\\Maya"]],
    [["slash"], ["a\\b"]],
    [["code"], ["`hello`"]],
    [["markup"], ["**bold**"]],
    [["url"], ["https://example.com/path?q=1"]],
    [["n"], ["1"], ["2"], ["3"]],
]


def make_roundtrip(rows):
    def test(self):
        self.assertEqual(parse(render(rows)), rows)
    return test


for number, example in enumerate(ROUNDTRIPS, 1):
    setattr(BaselineTests, f"test_roundtrip_{number:02d}", make_roundtrip(example))
