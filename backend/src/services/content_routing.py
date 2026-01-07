"""
Content routing services for RAG access to generated book content
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import re
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ContentRouter:
    """
    Service to route content requests for RAG system
    """

    def __init__(self, content_dir: str = "generated_content"):
        """
        Initialize the content router

        Args:
            content_dir: Directory containing generated content
        """
        self.content_dir = Path(content_dir)
        self.content_cache = {}
        self._load_content_cache()

    def _load_content_cache(self) -> None:
        """
        Load content into cache for faster access
        """
        logger.info(f"Loading content from {self.content_dir} into cache...")

        if not self.content_dir.exists():
            logger.warning(f"Content directory does not exist: {self.content_dir}")
            return

        # Walk through the content directory and cache all markdown files
        for md_file in self.content_dir.rglob("*.md"):
            try:
                relative_path = str(md_file.relative_to(self.content_dir))
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract metadata from the file
                metadata = self._extract_metadata(content, relative_path)

                self.content_cache[relative_path] = {
                    "content": content,
                    "metadata": metadata,
                    "last_modified": md_file.stat().st_mtime,
                    "size": len(content)
                }
            except Exception as e:
                logger.warning(f"Error loading content from {md_file}: {e}")

        logger.info(f"Loaded {len(self.content_cache)} content items into cache")

    def _extract_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from content file

        Args:
            content: Content string
            file_path: File path for context

        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            "file_path": file_path,
            "module": self._extract_module_from_path(file_path),
            "chapter": self._extract_chapter_from_path(file_path),
            "title": self._extract_title(content),
            "sections": self._extract_sections(content),
            "word_count": len(content.split()),
            "hash": hashlib.md5(content.encode()).hexdigest()
        }

        return metadata

    def _extract_module_from_path(self, file_path: str) -> str:
        """
        Extract module name from file path

        Args:
            file_path: File path string

        Returns:
            Module name
        """
        parts = file_path.split('/')
        for part in parts:
            if part.startswith("module_"):
                return part
        return "unknown_module"

    def _extract_chapter_from_path(self, file_path: str) -> str:
        """
        Extract chapter name from file path

        Args:
            file_path: File path string

        Returns:
            Chapter name
        """
        parts = file_path.split('/')
        for part in parts:
            if part.startswith("chapter_"):
                return part
        return "unknown_chapter"

    def _extract_title(self, content: str) -> str:
        """
        Extract title from content (first heading)

        Args:
            content: Content string

        Returns:
            Extracted title
        """
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
        return "Untitled"

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extract sections from content

        Args:
            content: Content string

        Returns:
            List of section dictionaries
        """
        sections = []
        lines = content.split('\n')

        current_section = {"title": "Introduction", "content": ""}

        for line in lines:
            if line.strip().startswith('## '):
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)

                # Start new section
                current_section = {
                    "title": line.strip()[3:].strip(),
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"

        # Add the last section
        if current_section["content"].strip():
            sections.append(current_section)

        return sections

    async def get_content_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get content by its path

        Args:
            path: Path to the content file

        Returns:
            Content dictionary or None if not found
        """
        if path in self.content_cache:
            return self.content_cache[path]

        # If not in cache, try to load from file
        file_path = self.content_dir / path
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                metadata = self._extract_metadata(content, path)

                # Cache the content
                self.content_cache[path] = {
                    "content": content,
                    "metadata": metadata,
                    "last_modified": file_path.stat().st_mtime,
                    "size": len(content)
                }

                return self.content_cache[path]
            except Exception as e:
                logger.error(f"Error loading content from {file_path}: {e}")

        return None

    async def search_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for content containing the query string

        Args:
            query: Search query string

        Returns:
            List of matching content items with context
        """
        results = []
        query_lower = query.lower()

        for path, data in self.content_cache.items():
            content_lower = data["content"].lower()

            if query_lower in content_lower:
                # Find context around matches
                lines = data["content"].split('\n')
                matches = []

                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # Get context (2 lines before and after)
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = '\n'.join(lines[start:end])

                        matches.append({
                            "line_number": i + 1,
                            "context": context.strip(),
                            "relevance": self._calculate_relevance(query, context)
                        })

                if matches:
                    results.append({
                        "path": path,
                        "metadata": data["metadata"],
                        "matches": matches,
                        "content_preview": data["content"][:500] + "..." if len(data["content"]) > 500 else data["content"]
                    })

        # Sort by relevance
        results.sort(key=lambda x: max(match["relevance"] for match in x["matches"]), reverse=True)

        return results

    def _calculate_relevance(self, query: str, context: str) -> float:
        """
        Calculate relevance score for a match

        Args:
            query: Search query
            context: Context around the match

        Returns:
            Relevance score between 0 and 1
        """
        query_words = set(query.lower().split())
        context_lower = context.lower()

        # Count exact matches
        exact_matches = sum(1 for word in query_words if word in context_lower)

        # Calculate relevance based on matches and context length
        relevance = exact_matches / len(query_words) if query_words else 0

        # Boost for exact phrase matches
        if query.lower() in context_lower:
            relevance = min(1.0, relevance + 0.3)

        return relevance

    async def get_module_content(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all content for a specific module

        Args:
            module_id: ID of the module

        Returns:
            Module content dictionary or None if not found
        """
        module_content = {
            "module_id": module_id,
            "chapters": [],
            "total_content": ""
        }

        for path, data in self.content_cache.items():
            if data["metadata"]["module"] == module_id:
                if "chapter_" in path:  # It's a chapter
                    chapter_data = {
                        "path": path,
                        "metadata": data["metadata"],
                        "content": data["content"]
                    }
                    module_content["chapters"].append(chapter_data)
                    module_content["total_content"] += data["content"] + "\n\n"

        if module_content["chapters"]:
            return module_content

        return None

    async def get_chapter_content(self, module_id: str, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content for a specific chapter

        Args:
            module_id: ID of the module
            chapter_id: ID of the chapter

        Returns:
            Chapter content dictionary or None if not found
        """
        for path, data in self.content_cache.items():
            if (data["metadata"]["module"] == module_id and
                data["metadata"]["chapter"] == chapter_id):
                return {
                    "path": path,
                    "metadata": data["metadata"],
                    "content": data["content"],
                    "sections": data["metadata"]["sections"]
                }

        return None

    async def get_content_chunks(self, path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Split content into chunks for RAG processing

        Args:
            path: Path to the content file
            chunk_size: Size of each chunk in characters

        Returns:
            List of content chunks
        """
        content_data = await self.get_content_by_path(path)
        if not content_data:
            return []

        content = content_data["content"]
        chunks = []

        # Split content into chunks
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]

            # Try to split at sentence boundaries if possible
            if i + chunk_size < len(content):
                # Look for sentence endings near the boundary
                next_part = content[i + chunk_size:]
                sentence_end = next_part.find('. ')
                if 0 < sentence_end < 100:  # Within 100 chars
                    actual_end = i + chunk_size + sentence_end + 2
                    chunk = content[i:actual_end]

            chunk_data = {
                "chunk_id": f"{path}_chunk_{i // chunk_size}",
                "content": chunk,
                "metadata": {
                    **content_data["metadata"],
                    "chunk_index": i // chunk_size,
                    "total_chunks": (len(content) + chunk_size - 1) // chunk_size
                },
                "embedding_text": self._prepare_for_embedding(chunk, content_data["metadata"])
            }

            chunks.append(chunk_data)

        return chunks

    def _prepare_for_embedding(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Prepare content for embedding by combining content with relevant metadata

        Args:
            content: Content string
            metadata: Metadata dictionary

        Returns:
            Prepared text for embedding
        """
        # Combine content with relevant metadata for better embeddings
        prepared_text = f"Module: {metadata.get('module', 'Unknown')}\n"
        prepared_text += f"Chapter: {metadata.get('chapter', 'Unknown')}\n"
        prepared_text += f"Title: {metadata.get('title', 'Untitled')}\n\n"
        prepared_text += content

        return prepared_text

    async def update_content_cache(self) -> None:
        """
        Update the content cache by checking for file modifications
        """
        logger.info("Updating content cache...")

        updated_count = 0
        for md_file in self.content_dir.rglob("*.md"):
            try:
                relative_path = str(md_file.relative_to(self.content_dir))
                last_modified = md_file.stat().st_mtime

                # Check if file is newer than cached version
                if (relative_path not in self.content_cache or
                    last_modified > self.content_cache[relative_path]["last_modified"]):

                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    metadata = self._extract_metadata(content, relative_path)

                    self.content_cache[relative_path] = {
                        "content": content,
                        "metadata": metadata,
                        "last_modified": last_modified,
                        "size": len(content)
                    }

                    updated_count += 1
            except Exception as e:
                logger.warning(f"Error updating cache for {md_file}: {e}")

        logger.info(f"Updated {updated_count} items in content cache")


class RAGContentService:
    """
    Service to provide content for RAG system
    """

    def __init__(self, content_router: ContentRouter):
        """
        Initialize the RAG content service

        Args:
            content_router: Content router instance
        """
        self.content_router = content_router

    async def get_relevant_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most relevant content for a query

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of relevant content chunks
        """
        search_results = await self.content_router.search_content(query)

        # Flatten all matches into individual chunks
        all_chunks = []
        for result in search_results:
            for match in result["matches"]:
                chunk = {
                    "content": result["content_preview"],
                    "metadata": result["metadata"],
                    "relevance_score": match["relevance"],
                    "context": match["context"]
                }
                all_chunks.append(chunk)

        # Sort by relevance and return top_k
        all_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return all_chunks[:top_k]

    async def get_content_for_rag(self, query: str, context_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Get content formatted for RAG processing

        Args:
            query: Search query
            context_override: Optional context to use instead of searching

        Returns:
            Dictionary with content for RAG
        """
        if context_override:
            # Use the provided context directly
            return {
                "retrieved_content": [{
                    "content": context_override,
                    "metadata": {"source": "user_selected_text"},
                    "relevance_score": 1.0
                }],
                "query": query,
                "method": "context_override"
            }
        else:
            # Search for relevant content
            relevant_content = await self.get_relevant_content(query)
            return {
                "retrieved_content": relevant_content,
                "query": query,
                "method": "semantic_search"
            }

    async def get_module_overview(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an overview of a module for RAG context

        Args:
            module_id: ID of the module

        Returns:
            Module overview or None if not found
        """
        module_content = await self.content_router.get_module_content(module_id)
        if not module_content:
            return None

        # Create a summary of the module
        chapter_titles = [chap["metadata"]["title"] for chap in module_content["chapters"]]

        overview = {
            "module_id": module_id,
            "title": module_content["chapters"][0]["metadata"]["module"].replace("module_", "").replace("_", " ").title() if module_content["chapters"] else "Unknown",
            "chapters": chapter_titles,
            "total_chapters": len(chapter_titles),
            "content_summary": f"This module contains {len(chapter_titles)} chapters covering the fundamentals of the topic.",
            "full_content": module_content["total_content"]
        }

        return overview


# Example usage
async def main():
    """
    Example of how to use the content routing services
    """
    # Initialize content router
    router = ContentRouter(content_dir="generated_content")

    # Initialize RAG content service
    rag_service = RAGContentService(router)

    # Example usage
    print("Content router initialized!")
    print(f"Loaded {len(router.content_cache)} content items")

    # Example search
    results = await router.search_content("neural networks")
    print(f"Found {len(results)} results for 'neural networks'")


if __name__ == "__main__":
    asyncio.run(main())