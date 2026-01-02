"""
Advanced content chunking utilities for RAG system
"""
import hashlib
import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ChunkStrategy(Enum):
    """Different strategies for chunking content"""
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    MARKDOWN = "markdown"
    SENTENCE = "sentence"
    CHARACTER = "character"


@dataclass
class Chunk:
    """Data class representing a content chunk"""
    content: str
    index: int
    source_file: str
    start_idx: int
    end_idx: int
    hash: str
    metadata: Dict[str, Any]
    embedding_id: Optional[str] = None


class AdvancedChunker:
    """Advanced chunking utilities with multiple strategies"""

    def __init__(self, default_chunk_size: int = 1000, default_overlap: int = 200):
        self.default_chunk_size = default_chunk_size
        self.default_overlap = default_overlap

    def chunk_content(
        self,
        content: str,
        strategy: ChunkStrategy = ChunkStrategy.RECURSIVE,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None,
        source_file: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk content using the specified strategy

        Args:
            content: Content to chunk
            strategy: Chunking strategy to use
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            source_file: Source file identifier
            metadata: Additional metadata for chunks

        Returns:
            List of Chunk objects
        """
        chunk_size = chunk_size or self.default_chunk_size
        overlap = overlap or self.default_overlap
        metadata = metadata or {}

        if strategy == ChunkStrategy.RECURSIVE:
            return self._recursive_chunk(content, chunk_size, overlap, source_file, metadata)
        elif strategy == ChunkStrategy.SEMANTIC:
            return self._semantic_chunk(content, chunk_size, overlap, source_file, metadata)
        elif strategy == ChunkStrategy.MARKDOWN:
            return self._markdown_chunk(content, chunk_size, overlap, source_file, metadata)
        elif strategy == ChunkStrategy.SENTENCE:
            return self._sentence_chunk(content, chunk_size, overlap, source_file, metadata)
        elif strategy == ChunkStrategy.CHARACTER:
            return self._character_chunk(content, chunk_size, overlap, source_file, metadata)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

    def _recursive_chunk(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
        source_file: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Recursive chunking that respects document structure"""
        # First try to split by paragraphs
        paragraphs = content.split('\n\n')

        chunks = []
        current_chunk = ""
        current_start_idx = 0
        chunk_idx = 0

        for paragraph in paragraphs:
            # If paragraph is too big, split it further
            if len(paragraph) > chunk_size:
                # Split large paragraph into sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                sentence_chunks = self._chunk_sentences(
                    sentences, chunk_size, overlap, current_start_idx
                )

                for sent_chunk in sentence_chunks:
                    chunk = Chunk(
                        content=sent_chunk.strip(),
                        index=chunk_idx,
                        source_file=source_file,
                        start_idx=current_start_idx,
                        end_idx=current_start_idx + len(sent_chunk),
                        hash=hashlib.md5(sent_chunk.encode()).hexdigest(),
                        metadata=metadata.copy()
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                    current_start_idx += len(sent_chunk)
            else:
                # Check if adding this paragraph would exceed chunk size
                if len(current_chunk) + len(paragraph) <= chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    # Save current chunk
                    if current_chunk.strip():
                        chunk = Chunk(
                            content=current_chunk.strip(),
                            index=chunk_idx,
                            source_file=source_file,
                            start_idx=current_start_idx,
                            end_idx=current_start_idx + len(current_chunk),
                            hash=hashlib.md5(current_chunk.encode()).hexdigest(),
                            metadata=metadata.copy()
                        )
                        chunks.append(chunk)
                        chunk_idx += 1

                    # Start new chunk with overlap
                    if overlap > 0 and len(current_chunk) > overlap:
                        overlap_text = current_chunk[-overlap:]
                        current_chunk = overlap_text + paragraph + "\n\n"
                        current_start_idx = current_start_idx + len(current_chunk) - len(overlap_text)
                    else:
                        current_chunk = paragraph + "\n\n"
                        current_start_idx = current_start_idx + len(current_chunk)

        # Add final chunk
        if current_chunk.strip():
            chunk = Chunk(
                content=current_chunk.strip(),
                index=chunk_idx,
                source_file=source_file,
                start_idx=current_start_idx,
                end_idx=current_start_idx + len(current_chunk),
                hash=hashlib.md5(current_chunk.encode()).hexdigest(),
                metadata=metadata.copy()
            )
            chunks.append(chunk)

        return chunks

    def _chunk_sentences(
        self,
        sentences: List[str],
        chunk_size: int,
        overlap: int,
        start_idx: int
    ) -> List[str]:
        """Helper method to chunk sentences"""
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Handle overlap
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + sentence + " "
                else:
                    current_chunk = sentence + " "

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _semantic_chunk(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
        source_file: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Semantic chunking that tries to keep related content together"""
        # This would typically use embeddings or NLP to identify semantic boundaries
        # For now, we'll implement a rule-based approach

        # Split on major document sections first
        sections = re.split(r'\n\s*#{1,3}\s+', content)

        chunks = []
        chunk_idx = 0
        current_start_idx = 0

        for section in sections:
            if section.strip():
                # If section is small enough, keep as is
                if len(section) <= chunk_size:
                    chunk = Chunk(
                        content=section.strip(),
                        index=chunk_idx,
                        source_file=source_file,
                        start_idx=current_start_idx,
                        end_idx=current_start_idx + len(section),
                        hash=hashlib.md5(section.encode()).hexdigest(),
                        metadata=metadata.copy()
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                    current_start_idx += len(section)
                else:
                    # Split large section using recursive approach
                    sub_chunks = self._recursive_chunk(
                        section, chunk_size, overlap, source_file, metadata
                    )
                    for sub_chunk in sub_chunks:
                        sub_chunk.index = chunk_idx
                        sub_chunk.start_idx = current_start_idx + sub_chunk.start_idx
                        sub_chunk.end_idx = current_start_idx + sub_chunk.end_idx
                        chunks.append(sub_chunk)
                        chunk_idx += 1

        return chunks

    def _markdown_chunk(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
        source_file: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Chunk markdown content while preserving structure"""
        # Split by markdown headers
        header_pattern = r'(^\s*#{1,6}\s+.*?$)'
        parts = re.split(header_pattern, content, flags=re.MULTILINE)

        chunks = []
        chunk_idx = 0
        current_start_idx = 0

        # Process parts in pairs (header, content)
        for i in range(0, len(parts), 2):
            header = parts[i] if i < len(parts) else ""
            content_part = parts[i + 1] if i + 1 < len(parts) else ""

            # Combine header with content
            full_part = header + content_part

            if len(full_part) <= chunk_size:
                chunk = Chunk(
                    content=full_part.strip(),
                    index=chunk_idx,
                    source_file=source_file,
                    start_idx=current_start_idx,
                    end_idx=current_start_idx + len(full_part),
                    hash=hashlib.md5(full_part.encode()).hexdigest(),
                    metadata=metadata.copy()
                )
                chunks.append(chunk)
                chunk_idx += 1
                current_start_idx += len(full_part)
            else:
                # Split large section
                sub_chunks = self._recursive_chunk(
                    full_part, chunk_size, overlap, source_file, metadata
                )
                for sub_chunk in sub_chunks:
                    sub_chunk.index = chunk_idx
                    sub_chunk.start_idx = current_start_idx + sub_chunk.start_idx
                    sub_chunk.end_idx = current_start_idx + sub_chunk.end_idx
                    chunks.append(sub_chunk)
                    chunk_idx += 1

        return chunks

    def _sentence_chunk(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
        source_file: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Chunk content by sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', content)

        chunks = []
        current_chunk = ""
        current_start_idx = 0
        chunk_idx = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunk = Chunk(
                        content=current_chunk.strip(),
                        index=chunk_idx,
                        source_file=source_file,
                        start_idx=current_start_idx,
                        end_idx=current_start_idx + len(current_chunk),
                        hash=hashlib.md5(current_chunk.encode()).hexdigest(),
                        metadata=metadata.copy()
                    )
                    chunks.append(chunk)
                    chunk_idx += 1

                # Handle overlap
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + sentence + " "
                    current_start_idx = current_start_idx + len(current_chunk) - len(overlap_text)
                else:
                    current_chunk = sentence + " "
                    current_start_idx = current_start_idx + len(current_chunk)

        # Add final chunk
        if current_chunk.strip():
            chunk = Chunk(
                content=current_chunk.strip(),
                index=chunk_idx,
                source_file=source_file,
                start_idx=current_start_idx,
                end_idx=current_start_idx + len(current_chunk),
                hash=hashlib.md5(current_chunk.encode()).hexdigest(),
                metadata=metadata.copy()
            )
            chunks.append(chunk)

        return chunks

    def _character_chunk(
        self,
        content: str,
        chunk_size: int,
        overlap: int,
        source_file: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Simple character-based chunking"""
        chunks = []
        chunk_idx = 0
        start_idx = 0

        while start_idx < len(content):
            end_idx = min(start_idx + chunk_size, len(content))
            chunk_content = content[start_idx:end_idx]

            chunk = Chunk(
                content=chunk_content,
                index=chunk_idx,
                source_file=source_file,
                start_idx=start_idx,
                end_idx=end_idx,
                hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                metadata=metadata.copy()
            )
            chunks.append(chunk)

            # Move to next chunk position with overlap
            start_idx = end_idx - overlap if overlap < end_idx else end_idx
            chunk_idx += 1

        return chunks

    def merge_chunks(self, chunks: List[Chunk], max_chunk_size: int) -> List[Chunk]:
        """Merge small chunks to approach max_chunk_size"""
        if not chunks:
            return []

        merged = [chunks[0]]

        for chunk in chunks[1:]:
            last_chunk = merged[-1]

            # If combining with last chunk doesn't exceed max size, merge
            if len(last_chunk.content) + len(chunk.content) <= max_chunk_size:
                merged[-1] = Chunk(
                    content=last_chunk.content + " " + chunk.content,
                    index=last_chunk.index,
                    source_file=last_chunk.source_file,
                    start_idx=last_chunk.start_idx,
                    end_idx=chunk.end_idx,
                    hash=hashlib.md5((last_chunk.content + chunk.content).encode()).hexdigest(),
                    metadata={**last_chunk.metadata, **chunk.metadata}
                )
            else:
                # Keep as separate chunk
                merged.append(chunk)

        # Re-index the merged chunks
        for i, chunk in enumerate(merged):
            chunk.index = i

        return merged


# Backward compatibility function
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Backward compatible function for chunking text
    """
    chunker = AdvancedChunker()
    chunks = chunker.chunk_content(
        content=text,
        strategy=ChunkStrategy.RECURSIVE,
        chunk_size=chunk_size,
        overlap=overlap
    )

    # Convert to the old format for compatibility
    result = []
    for chunk in chunks:
        result.append({
            "content": chunk.content,
            "index": chunk.index,
            "source_file": chunk.source_file,
            "start_idx": chunk.start_idx,
            "end_idx": chunk.end_idx,
            "hash": chunk.hash,
            "metadata": chunk.metadata
        })

    return result


def chunk_markdown_document(
    markdown_content: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    source_file: str = ""
) -> List[Dict[str, Any]]:
    """
    Backward compatible function for chunking markdown documents
    """
    chunker = AdvancedChunker()
    chunks = chunker.chunk_content(
        content=markdown_content,
        strategy=ChunkStrategy.MARKDOWN,
        chunk_size=chunk_size,
        overlap=overlap,
        source_file=source_file
    )

    # Convert to the old format for compatibility
    result = []
    for chunk in chunks:
        result.append({
            "content": chunk.content,
            "index": chunk.index,
            "source_file": chunk.source_file,
            "start_idx": chunk.start_idx,
            "end_idx": chunk.end_idx,
            "hash": chunk.hash,
            "metadata": chunk.metadata
        })

    return result