import re
from typing import List


def normalize_text(text: str) -> str:
    """Normalizes text by lowercasing and removing non-alphanumeric characters.

    Args:
        text (str): The input text string.

    Returns:
        str: The normalized text string.
    """
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into chunks with specified size and overlap.

    Args:
        text (str): The text to be chunked.
        chunk_size (int): The number of tokens per chunk.
        overlap (int): The number of overlapping tokens between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    words = text.split()
    total_words = len(words)
    chunks = []
    start = 0

    while start < total_words:
        end = min(start + chunk_size, total_words)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
