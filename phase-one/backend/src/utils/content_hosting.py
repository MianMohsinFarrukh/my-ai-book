"""
Local content hosting server for generated book content
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn

logger = logging.getLogger(__name__)

class ContentHostingServer:
    """
    Local server to host generated book content for RAG access
    """

    def __init__(
        self,
        content_dir: str = "generated_content",
        host: str = "127.0.0.1",
        port: int = 8080
    ):
        """
        Initialize the content hosting server

        Args:
            content_dir: Directory containing generated content
            host: Host for the server
            port: Port for the server
        """
        self.content_dir = Path(content_dir)
        self.host = host
        self.port = port
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """
        Create FastAPI application for content hosting

        Returns:
            FastAPI application instance
        """
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info(f"Content hosting server starting on {self.host}:{self.port}")
            yield
            # Shutdown
            logger.info("Content hosting server shutting down")

        app = FastAPI(
            title="Book Content Hosting API",
            description="API for serving generated book content",
            version="0.1.0",
            lifespan=lifespan
        )

        # Mount static files
        if self.content_dir.exists():
            app.mount("/content", StaticFiles(directory=str(self.content_dir)), name="content")
        else:
            logger.warning(f"Content directory does not exist: {self.content_dir}")

        # Add API endpoints
        self._add_endpoints(app)

        return app

    def _add_endpoints(self, app: FastAPI) -> None:
        """
        Add API endpoints to the application

        Args:
            app: FastAPI application instance
        """
        @app.get("/")
        async def root():
            return {"message": "Book Content Hosting Server", "status": "running"}

        @app.get("/api/v1/content/structure")
        async def get_content_structure():
            """
            Get the structure of the generated content
            """
            try:
                structure = self._scan_content_structure()
                return JSONResponse(content=structure)
            except Exception as e:
                logger.error(f"Error getting content structure: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/v1/content/search")
        async def search_content(query: str):
            """
            Search for content in the generated book
            """
            try:
                results = self._search_content(query)
                return JSONResponse(content={"results": results, "query": query})
            except Exception as e:
                logger.error(f"Error searching content: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/v1/content/modules")
        async def get_modules():
            """
            Get list of available modules
            """
            try:
                modules = self._get_modules_list()
                return JSONResponse(content={"modules": modules})
            except Exception as e:
                logger.error(f"Error getting modules: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/v1/content/module/{module_id}")
        async def get_module(module_id: str):
            """
            Get specific module content
            """
            try:
                module = self._get_module_content(module_id)
                return JSONResponse(content=module)
            except Exception as e:
                logger.error(f"Error getting module {module_id}: {e}")
                raise HTTPException(status_code=404, detail=f"Module {module_id} not found")

        @app.get("/api/v1/content/chapter/{module_id}/{chapter_id}")
        async def get_chapter(module_id: str, chapter_id: str):
            """
            Get specific chapter content
            """
            try:
                chapter = self._get_chapter_content(module_id, chapter_id)
                return JSONResponse(content=chapter)
            except Exception as e:
                logger.error(f"Error getting chapter {chapter_id} from module {module_id}: {e}")
                raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found in module {module_id}")

    def _scan_content_structure(self) -> Dict[str, Any]:
        """
        Scan the content directory and return its structure

        Returns:
            Dictionary representing content structure
        """
        if not self.content_dir.exists():
            return {"modules": [], "total_files": 0, "content_dir": str(self.content_dir)}

        structure = {
            "content_dir": str(self.content_dir),
            "total_files": 0,
            "modules": []
        }

        for module_dir in self.content_dir.iterdir():
            if module_dir.is_dir() and module_dir.name.startswith("module_"):
                module_info = {
                    "id": module_dir.name,
                    "name": module_dir.name.replace("module_", "").replace("_", " ").title(),
                    "path": str(module_dir.relative_to(self.content_dir)),
                    "chapters": []
                }

                for chapter_dir in module_dir.iterdir():
                    if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                        chapter_info = {
                            "id": chapter_dir.name,
                            "name": chapter_dir.name.replace("chapter_", "").replace("_", " ").title(),
                            "path": str(chapter_dir.relative_to(self.content_dir)),
                            "files": []
                        }

                        # Count files in chapter directory
                        for file_path in chapter_dir.rglob("*"):
                            if file_path.is_file():
                                chapter_info["files"].append({
                                    "name": file_path.name,
                                    "path": str(file_path.relative_to(self.content_dir)),
                                    "size": file_path.stat().st_size
                                })
                                structure["total_files"] += 1

                        module_info["chapters"].append(chapter_info)
                        structure["total_files"] += len(chapter_info["files"])

                structure["modules"].append(module_info)

        return structure

    def _search_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for content containing the query string

        Args:
            query: Search query string

        Returns:
            List of matching content items
        """
        results = []

        if not self.content_dir.exists():
            return results

        # Search through markdown files for the query
        for md_file in self.content_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if query.lower() in content.lower():
                    # Extract context around the match
                    lines = content.split('\n')
                    matching_lines = []

                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            # Include context (2 lines before and after)
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])

                            matching_lines.append({
                                "line_number": i + 1,
                                "content": context.strip(),
                                "file_path": str(md_file.relative_to(self.content_dir))
                            })

                    if matching_lines:
                        results.append({
                            "file": str(md_file.relative_to(self.content_dir)),
                            "matches": matching_lines,
                            "module": self._extract_module_from_path(md_file),
                            "chapter": self._extract_chapter_from_path(md_file)
                        })
            except Exception as e:
                logger.warning(f"Error searching in {md_file}: {e}")

        return results

    def _extract_module_from_path(self, file_path: Path) -> str:
        """
        Extract module name from file path

        Args:
            file_path: Path to the file

        Returns:
            Module name
        """
        parts = file_path.relative_to(self.content_dir).parts
        for part in parts:
            if part.startswith("module_"):
                return part
        return "unknown_module"

    def _extract_chapter_from_path(self, file_path: Path) -> str:
        """
        Extract chapter name from file path

        Args:
            file_path: Path to the file

        Returns:
            Chapter name
        """
        parts = file_path.relative_to(self.content_dir).parts
        for part in parts:
            if part.startswith("chapter_"):
                return part
        return "unknown_chapter"

    def _get_modules_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available modules

        Returns:
            List of module information
        """
        modules = []

        if not self.content_dir.exists():
            return modules

        for module_dir in self.content_dir.iterdir():
            if module_dir.is_dir() and module_dir.name.startswith("module_"):
                # Try to read module information from index.md
                index_file = module_dir / "index.md"
                module_info = {
                    "id": module_dir.name,
                    "name": module_dir.name.replace("module_", "").replace("_", " ").title(),
                    "path": str(module_dir.relative_to(self.content_dir)),
                    "has_index": index_file.exists()
                }

                if index_file.exists():
                    try:
                        with open(index_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract title from frontmatter or first heading
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip().startswith('# '):
                                    module_info["title"] = line.strip()[2:]
                                    break
                    except Exception as e:
                        logger.warning(f"Error reading module index {index_file}: {e}")

                modules.append(module_info)

        return modules

    def _get_module_content(self, module_id: str) -> Dict[str, Any]:
        """
        Get content of a specific module

        Args:
            module_id: ID of the module

        Returns:
            Module content
        """
        module_path = self.content_dir / module_id

        if not module_path.exists():
            raise FileNotFoundError(f"Module {module_id} not found")

        # Read module index file
        index_file = module_path / "index.md"
        content = ""

        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()

        return {
            "id": module_id,
            "name": module_id.replace("module_", "").replace("_", " ").title(),
            "path": str(module_path.relative_to(self.content_dir)),
            "content": content,
            "chapters": self._get_chapters_list(module_id)
        }

    def _get_chapters_list(self, module_id: str) -> List[Dict[str, Any]]:
        """
        Get list of chapters in a module

        Args:
            module_id: ID of the module

        Returns:
            List of chapter information
        """
        module_path = self.content_dir / module_id
        chapters = []

        if not module_path.exists():
            return chapters

        for chapter_dir in module_path.iterdir():
            if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                index_file = chapter_dir / "index.md"
                chapter_info = {
                    "id": chapter_dir.name,
                    "name": chapter_dir.name.replace("chapter_", "").replace("_", " ").title(),
                    "path": str(chapter_dir.relative_to(self.content_dir)),
                    "has_content": index_file.exists()
                }

                if index_file.exists():
                    try:
                        with open(index_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract title from content
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip().startswith('# '):
                                    chapter_info["title"] = line.strip()[2:]
                                    break
                    except Exception as e:
                        logger.warning(f"Error reading chapter index {index_file}: {e}")

                chapters.append(chapter_info)

        return chapters

    def _get_chapter_content(self, module_id: str, chapter_id: str) -> Dict[str, Any]:
        """
        Get content of a specific chapter

        Args:
            module_id: ID of the module
            chapter_id: ID of the chapter

        Returns:
            Chapter content
        """
        chapter_path = self.content_dir / module_id / chapter_id
        index_file = chapter_path / "index.md"

        if not index_file.exists():
            raise FileNotFoundError(f"Chapter {chapter_id} not found in module {module_id}")

        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "module_id": module_id,
            "chapter_id": chapter_id,
            "name": chapter_id.replace("chapter_", "").replace("_", " ").title(),
            "path": str(chapter_path.relative_to(self.content_dir)),
            "content": content
        }

    def run(self, debug: bool = False):
        """
        Start the content hosting server

        Args:
            debug: Enable debug mode
        """
        logger.info(f"Starting content hosting server on {self.host}:{self.port}")
        logger.info(f"Serving content from: {self.content_dir}")

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug,
            log_level="info"
        )


# Example usage
async def main():
    """
    Example of how to use the ContentHostingServer
    """
    # Create and start the content hosting server
    server = ContentHostingServer(
        content_dir="generated_content",
        host="127.0.0.1",
        port=8080
    )

    # You can run this in a separate thread or process in a real application
    # For this example, we'll just show how to start it
    print("Content hosting server ready to run!")
    print("Access the API at: http://127.0.0.1:8080")
    print("Content structure API: http://127.0.0.1:8080/api/v1/content/structure")


if __name__ == "__main__":
    asyncio.run(main())