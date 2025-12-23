"""
Text chunking utility for splitting book content into manageable pieces
"""
import re
from typing import List
from app.config import settings


def chunk_text(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text content into chunks of approximately chunk_size tokens with overlap.

    Args:
        content: The text content to be chunked
        chunk_size: Target size of each chunk in tokens/characters
        overlap: Number of tokens/characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    # Use a simple approach based on character count for now
    # In a real implementation, you might want to use tokenization
    # libraries like tiktoken for more accurate token counts

    # First, break the content into sentences to avoid breaking in the middle of sentences
    sentences = re.split(r'(?<=[.!?]) +', content)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Check if adding this sentence would exceed the chunk size
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            # If the current chunk is not empty, save it
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # Start a new chunk with the current sentence
            # If the sentence itself is longer than chunk_size, we'll need to break it
            if len(sentence) > chunk_size:
                # Break long sentences into smaller pieces
                sentence_chunks = _break_long_sentence(sentence, chunk_size)
                for i, sentence_chunk in enumerate(sentence_chunks):
                    if i == len(sentence_chunks) - 1:
                        # Last piece becomes the current chunk
                        current_chunk = sentence_chunk + " "
                    else:
                        # Add to chunks list
                        chunks.append(sentence_chunk)
            else:
                current_chunk = sentence + " "

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Apply overlap if requested
    if overlap > 0 and len(chunks) > 1:
        chunks = _apply_overlap(chunks, overlap)

    return chunks


def _break_long_sentence(sentence: str, chunk_size: int) -> List[str]:
    """
    Break a sentence that is longer than the chunk size into smaller pieces.

    Args:
        sentence: The long sentence to break
        chunk_size: Maximum size for each piece

    Returns:
        List of sentence pieces
    """
    if len(sentence) <= chunk_size:
        return [sentence]

    pieces = []
    start = 0

    while start < len(sentence):
        end = start + chunk_size

        # If we're not at the end, try to break at a space to avoid cutting words
        if end < len(sentence):
            # Look for the last space within the chunk
            last_space = sentence.rfind(' ', start, end)
            if last_space != -1 and last_space > start:
                end = last_space

        piece = sentence[start:end].strip()
        if piece:  # Only add non-empty pieces
            pieces.append(piece)

        start = end

        # If we couldn't find a space, force break at chunk_size
        if start == start + chunk_size and end == start + chunk_size:
            start += 1  # Move by one character to avoid infinite loop

    return pieces


def _apply_overlap(chunks: List[str], overlap: int) -> List[str]:
    """
    Apply overlap between consecutive chunks.

    Args:
        chunks: List of text chunks
        overlap: Number of characters to overlap

    Returns:
        List of chunks with overlap applied
    """
    if len(chunks) <= 1 or overlap <= 0:
        return chunks

    result = []

    for i, chunk in enumerate(chunks):
        if i > 0:
            # Get the overlap from the previous chunk
            prev_chunk = chunks[i-1]
            overlap_text = prev_chunk[-overlap:] if len(prev_chunk) >= overlap else prev_chunk
            # Add the overlap to the current chunk
            chunk = overlap_text + " " + chunk

        result.append(chunk)

    return result


def validate_chunk_size(chunk_size: int, max_size: int = 1000, min_size: int = 100) -> bool:
    """
    Validate that the chunk size is within acceptable bounds.

    Args:
        chunk_size: The proposed chunk size
        max_size: Maximum allowed chunk size
        min_size: Minimum allowed chunk size

    Returns:
        True if valid, False otherwise
    """
    return min_size <= chunk_size <= max_size


def calculate_chunk_stats(chunks: List[str]) -> dict:
    """
    Calculate statistics about the chunks.

    Args:
        chunks: List of text chunks

    Returns:
        Dictionary with statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "total_chars": 0
        }

    lengths = [len(chunk) for chunk in chunks]

    return {
        "total_chunks": len(chunks),
        "avg_length": sum(lengths) / len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "total_chars": sum(lengths)
    }