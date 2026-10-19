"""Render a rectangular sequence of strings as a Markdown table."""


def render(rows):
    if not rows:
        return ""
    width = len(rows[0])
    if not width or any(len(row) != width for row in rows):
        raise ValueError("Expected a nonempty rectangular table")
    if any(not isinstance(cell, str) for row in rows for cell in row):
        raise TypeError("Cells must be strings")
    if any("\n" in cell or "\r" in cell for row in rows for cell in row):
        raise ValueError("Multiline cells are unsupported")
    lines = ["| " + " | ".join(rows[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(lines)
