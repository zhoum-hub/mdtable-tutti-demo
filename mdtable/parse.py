"""Parse the compact Markdown table format emitted by render."""


def _split_cells(text):
    """Split row contents on unescaped pipes.

    A backslash escapes a following backslash or pipe, so ``\\|`` is a literal
    pipe and ``\\\\`` is a literal backslash. Any other backslash is literal,
    matching ``_escape`` in render while leaving ordinary text such as
    ``a\\b`` untouched.
    """
    cells = []
    current = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\\" and index + 1 < length and text[index + 1] in "\\|":
            current.append(text[index + 1])
            index += 2
        elif char == "|":
            cells.append("".join(current))
            current = []
            index += 1
        else:
            current.append(char)
            index += 1
    cells.append("".join(current))
    return [cell.strip() for cell in cells]


def parse(text):
    if not text.strip():
        return []
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("Expected a header and separator")
    rows = []
    for index, line in enumerate(lines):
        if not line.startswith("|") or not line.endswith("|"):
            raise ValueError("Rows must have leading and trailing pipes")
        cells = _split_cells(line[1:-1])
        if index == 1:
            if len(cells) != len(rows[0]) or any(cell != "---" for cell in cells):
                raise ValueError("Invalid separator")
            continue
        if rows and len(cells) != len(rows[0]):
            raise ValueError("Inconsistent number of columns")
        rows.append(cells)
    return rows
