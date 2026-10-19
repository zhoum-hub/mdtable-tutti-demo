# Changelog

## Unreleased

- Support literal pipe characters in table cells. Renderer escapes backslashes
  and pipes; parser unescapes them, so cells round-trip without changing table
  structure. A backslash before any other character stays literal, preserving
  existing hand-written input.

## 0.4.2 (sample baseline)

- Validate rectangular tables and single-line string cells.

## 0.4.1 (sample history)

- Document the compact Markdown table format.

## 0.4.0 (sample history)

- Add the initial renderer and parser.
