"""Parse the compact Markdown table format emitted by render."""


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
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if index == 1:
            if len(cells) != len(rows[0]) or any(cell != "---" for cell in cells):
                raise ValueError("Invalid separator")
            continue
        if rows and len(cells) != len(rows[0]):
            raise ValueError("Inconsistent number of columns")
        rows.append(cells)
    return rows
