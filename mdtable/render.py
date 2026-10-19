"""Render a rectangular sequence of strings as a Markdown table."""


def _escape(cell):
    """Backslash-escape the cell's own backslashes, then its pipes."""
    return cell.replace("\\", "\\\\").replace("|", "\\|")


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
    escaped_rows = [[_escape(cell) for cell in row] for row in rows]
    lines = ["| " + " | ".join(escaped_rows[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in escaped_rows[1:])
    return "\n".join(lines)
