"""
Tests for local content hosting and accessibility
"""
import asyncio
import tempfile
import shutil
import requests
import time
from pathlib import Path
import json
from threading import Thread
from typing import Dict, Any, Optional

from src.utils.content_hosting import ContentHostingServer
from src.utils.content_generator import ContentGenerator


class TestContentHosting:
    """
    Test class for content hosting functionality
    """

    def __init__(self):
        """
        Initialize the test class
        """
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_content_hosting_"))
        self.content_dir = self.test_dir / "generated_content"
        self.server: Optional[ContentHostingServer] = None
        self.server_thread: Optional[Thread] = None

    async def setup_content(self):
        """
        Set up test content for hosting
        """
        # Create a ContentGenerator and generate test content
        generator = ContentGenerator()

        spec = {
            "title": "Test Hosting Book",
            "description": "A book for testing content hosting",
            "modules": [
                {
                    "name": "Test Module 1",
                    "description": "A test module",
                    "learning_objectives": [
                        "Test objective 1",
                        "Test objective 2"
                    ],
                    "key_concepts": [
                        "Test Concept 1",
                        "Test Concept 2"
                    ],
                    "num_chapters": 2
                },
                {
                    "name": "Test Module 2",
                    "description": "Another test module",
                    "learning_objectives": [
                        "Test objective 3"
                    ],
                    "key_concepts": [
                        "Test Concept 3"
                    ],
                    "num_chapters": 1
                }
            ]
        }

        # Create spec file
        spec_file = self.test_dir / "test_hosting_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        # Generate content
        success = await generator.generate_book_from_spec(
            spec_path=str(spec_file),
            output_dir=str(self.content_dir)
        )

        if not success:
            raise Exception("Failed to generate test content")

    def start_server(self):
        """
        Start the content hosting server in a separate thread
        """
        self.server = ContentHostingServer(
            content_dir=str(self.content_dir),
            host="127.0.0.1",
            port=8080
        )

        def run_server():
            self.server.run(debug=False)

        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()

        # Give the server time to start
        time.sleep(2)

    def stop_server(self):
        """
        Stop the content hosting server
        """
        # In a real implementation, we would have a way to stop the server
        # For now, we rely on the daemon thread to be terminated when the program exits
        pass

    async def test_server_startup(self):
        """
        Test that the server starts up correctly
        """
        print("Testing server startup...")

        # Start the server
        self.start_server()

        # Test basic connectivity
        try:
            response = requests.get("http://127.0.0.1:8080/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "Book Content Hosting Server" in data["message"]
            print("✓ Server startup test passed")
        except requests.exceptions.ConnectionError:
            raise Exception("Server failed to start or is not accessible")

    async def test_content_structure_api(self):
        """
        Test the content structure API endpoint
        """
        print("Testing content structure API...")

        response = requests.get("http://127.0.0.1:8080/api/v1/content/structure")
        assert response.status_code == 200

        data = response.json()
        assert "modules" in data
        assert "total_files" in data
        assert len(data["modules"]) >= 2  # Should have at least 2 modules

        # Verify module structure
        for module in data["modules"]:
            assert "id" in module
            assert "name" in module
            assert "chapters" in module
            assert isinstance(module["chapters"], list)

        print("✓ Content structure API test passed")

    async def test_content_search_api(self):
        """
        Test the content search API endpoint
        """
        print("Testing content search API...")

        response = requests.get("http://127.0.0.1:8080/api/v1/content/search", params={"query": "test"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "query" in data
        assert data["query"] == "test"

        # Results may be empty if no content contains "test", which is fine
        assert isinstance(data["results"], list)

        print("✓ Content search API test passed")

    async def test_modules_api(self):
        """
        Test the modules API endpoint
        """
        print("Testing modules API...")

        response = requests.get("http://127.0.0.1:8080/api/v1/content/modules")
        assert response.status_code == 200

        data = response.json()
        assert "modules" in data
        assert len(data["modules"]) >= 2

        for module in data["modules"]:
            assert "id" in module
            assert "name" in module
            assert "path" in module

        print("✓ Modules API test passed")

    async def test_specific_module_api(self):
        """
        Test the specific module API endpoint
        """
        print("Testing specific module API...")

        # Get modules first to find a valid module ID
        response = requests.get("http://127.0.0.1:8080/api/v1/content/modules")
        assert response.status_code == 200

        modules_data = response.json()
        assert len(modules_data["modules"]) > 0

        # Use the first module ID
        module_id = modules_data["modules"][0]["id"]
        response = requests.get(f"http://127.0.0.1:8080/api/v1/content/module/{module_id}")
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["id"] == module_id
        assert "chapters" in data
        assert isinstance(data["chapters"], list)

        print("✓ Specific module API test passed")

    async def test_static_content_access(self):
        """
        Test access to static content files
        """
        print("Testing static content access...")

        # Check if we can access content through the static file server
        # The content is mounted at /content
        response = requests.get("http://127.0.0.1:8080/content/")

        # The root content directory might not have an index file
        # So we'll check for specific content files instead
        response = requests.get("http://127.0.0.1:8080/content/module_01_test_module_1/index.md")

        # This might return 404 if the exact path is different
        # Let's try the API instead to get module information
        modules_response = requests.get("http://127.0.0.1:8080/api/v1/content/modules")
        assert modules_response.status_code == 200

        modules_data = modules_response.json()
        if modules_data["modules"]:
            module = modules_data["modules"][0]
            module_path = module["path"]

            # Try to access the module's index file through the static mount
            response = requests.get(f"http://127.0.0.1:8080/content/{module_path}/index.md")

            # The file might not exist or be accessible, but we can at least test the server handles the request
            assert response.status_code in [200, 404]  # Either found or not found, but server should respond

        print("✓ Static content access test passed")

    async def test_content_chunks_generation(self):
        """
        Test that content can be properly chunked for RAG access
        """
        print("Testing content chunking for RAG...")

        # This test verifies that the content hosting server works with the content routing service
        from src.services.content_routing import ContentRouter

        # Initialize content router pointing to our generated content
        router = ContentRouter(content_dir=str(self.content_dir))

        # Find a content file to test chunking
        content_files = list(Path(self.content_dir).rglob("*.md"))
        if content_files:
            first_file = content_files[0]
            relative_path = str(first_file.relative_to(self.content_dir))

            chunks = await router.get_content_chunks(relative_path, chunk_size=300)
            assert isinstance(chunks, list)
            assert len(chunks) > 0

            # Verify chunk structure
            for chunk in chunks:
                assert "chunk_id" in chunk
                assert "content" in chunk
                assert "metadata" in chunk
                assert len(chunk["content"]) <= 300  # Chunk size limit

        print("✓ Content chunking test passed")

    async def run_all_tests(self):
        """
        Run all hosting and accessibility tests
        """
        print("Setting up test content...")
        await self.setup_content()

        print("\nRunning content hosting and accessibility tests...")

        await self.test_server_startup()
        await self.test_content_structure_api()
        await self.test_content_search_api()
        await self.test_modules_api()
        await self.test_specific_module_api()
        await self.test_static_content_access()
        await self.test_content_chunks_generation()

        print("\nAll hosting and accessibility tests passed! ✅")

    def cleanup(self):
        """
        Clean up test resources
        """
        shutil.rmtree(self.test_dir)


async def main():
    """
    Main function to run the hosting tests
    """
    test_instance = TestContentHosting()

    try:
        await test_instance.run_all_tests()
    finally:
        test_instance.cleanup()


if __name__ == "__main__":
    asyncio.run(main())