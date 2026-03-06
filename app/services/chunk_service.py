"""
Text chunking service — sliding-window word-based chunking with overlap.
"""

from app.config.settings import get_settings


def chunk_text(
    text: str,
    size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Parameters
    ----------
    text : str
        Source text to chunk.
    size : int, optional
        Number of words per chunk (default from settings).
    overlap : int, optional
        Number of overlapping words between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.
    """
    settings = get_settings()
    size = size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(size - overlap, 1)

    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
        # Stop if we've consumed all words
        if i + size >= len(words):
            break

    return chunks
