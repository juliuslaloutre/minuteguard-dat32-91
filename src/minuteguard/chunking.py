"""Line-preserving document chunking for bounded context windows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    first_line: int
    last_line: int


def split_text(text: str, *, max_chars: int = 12_000, overlap_lines: int = 2) -> list[TextChunk]:
    """Split on line boundaries and preserve global line numbers.

    ``max_chars`` is a conservative character budget rather than an exact token
    count. Very long individual lines remain intact so citations stay stable.
    """

    if max_chars < 200:
        raise ValueError("max_chars must be at least 200")
    if overlap_lines < 0:
        raise ValueError("overlap_lines cannot be negative")

    lines = text.splitlines()
    if not lines:
        return [TextChunk(text="", first_line=1, last_line=1)]

    chunks: list[TextChunk] = []
    start = 0
    while start < len(lines):
        end = start
        size = 0
        while end < len(lines):
            added = len(lines[end]) + (1 if end > start else 0)
            if end > start and size + added > max_chars:
                break
            size += added
            end += 1

        if end == start:
            end += 1

        chunks.append(
            TextChunk(
                text="\n".join(lines[start:end]),
                first_line=start + 1,
                last_line=end,
            )
        )
        if end == len(lines):
            break
        start = max(start + 1, end - overlap_lines)

    return chunks

