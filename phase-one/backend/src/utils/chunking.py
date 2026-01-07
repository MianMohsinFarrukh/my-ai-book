"""
Content chunking utilities
"""
import hashlib
from typing import List, Dict, Any, Tuple
import re


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    # Split text into sentences to avoid breaking them
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""
    current_start_idx = 0

    for sentence in sentences:
        # Check if adding this sentence would exceed chunk size
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            # If current chunk is not empty, save it
            if current_chunk.strip():
                chunk_data = {
                    "content": current_chunk.strip(),
                    "start_idx": current_start_idx,
                    "end_idx": current_start_idx + len(current_chunk),
                    "hash": hashlib.md5(current_chunk.encode()).hexdigest()
                }
                chunks.append(chunk_data)

            # Start a new chunk, possibly with overlap from the previous chunk
            if len(sentence) > chunk_size:
                # If the sentence itself is longer than chunk_size, split it
                words = sentence.split()
                current_chunk = ""
                current_start_idx = current_start_idx + len(current_chunk)

                for word in words:
                    if len(current_chunk) + len(word) <= chunk_size:
                        current_chunk += word + " "
                    else:
                        chunk_data = {
                            "content": current_chunk.strip(),
                            "start_idx": current_start_idx,
                            "end_idx": current_start_idx + len(current_chunk),
                            "hash": hashlib.md5(current_chunk.encode()).hexdigest()
                        }
                        chunks.append(chunk_data)

                        # For overlap, take the last part of the current chunk
                        overlap_start = max(0, len(current_chunk) - overlap)
                        current_chunk = current_chunk[overlap_start:] + word + " "
                        current_start_idx = current_start_idx + overlap_start

            else:
                # Use overlap from the end of the previous chunk
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + sentence + " "
                    current_start_idx = current_start_idx + len(current_chunk) - len(overlap_text)
                else:
                    current_chunk = sentence + " "
                    current_start_idx = current_start_idx + len(current_chunk)

    # Add the final chunk if it's not empty
    if current_chunk.strip():
        chunk_data = {
            "content": current_chunk.strip(),
            "start_idx": current_start_idx,
            "end_idx": current_start_idx + len(current_chunk),
            "hash": hashlib.md5(current_chunk.encode()).hexdigest()
        }
        chunks.append(chunk_data)

    # Add index to each chunk
    for i, chunk in enumerate(chunks):
        chunk["index"] = i

    return chunks


def chunk_markdown_document(markdown_content: str,
                          chunk_size: int = 1000,
                          overlap: int = 200,
                          source_file: str = "") -> List[Dict[str, Any]]:
    """
    Chunk a markdown document, preserving document structure
    """
    # Split by markdown headers to keep sections together when possible
    header_pattern = r'(^|\n)(#{1,6}\s+.*?)(\n|$)'
    parts = re.split(header_pattern, markdown_content)

    # Reconstruct the parts with headers
    sections = []
    current_section = ""

    for i, part in enumerate(parts):
        if re.match(header_pattern, '\n' + part.strip() + '\n' if part.strip() else '\n\n'):
            # This is a header
            if current_section.strip():
                sections.append(current_section.strip())
            current_section = part.strip()
        else:
            # This is content
            current_section += part

    if current_section.strip():
        sections.append(current_section.strip())

    # Now chunk each section
    all_chunks = []
    for section in sections:
        if section.strip():
            section_chunks = chunk_text(section, chunk_size, overlap)
            for chunk in section_chunks:
                chunk["source_file"] = source_file
                chunk["section"] = section[:100] + "..." if len(section) > 100 else section  # First 100 chars as section identifier
                all_chunks.append(chunk)

    # Re-index all chunks
    for i, chunk in enumerate(all_chunks):
        chunk["index"] = i

    return all_chunks


def calculate_chunk_hash(content: str, source_file: str, chunk_index: int) -> str:
    """
    Calculate a hash for a content chunk to detect changes
    """
    hash_input = f"{source_file}:{chunk_index}:{content}"
    return hashlib.md5(hash_input.encode()).hexdigest()