"""
Tests for the automatic content generation pipeline
"""
import asyncio
import tempfile
import shutil
from pathlib import Path
import json
import pytest
from typing import Dict, Any

from src.utils.book_generator import BookGenerator
from src.utils.chapter_generator import ChapterGenerator
from src.utils.content_generator import ContentGenerator
from src.utils.content_validator import ContentValidator, ValidationResult
from src.services.content_routing import ContentRouter, RAGContentService

class TestContentGenerationPipeline:
    """
    Test class for the content generation pipeline
    """

    def setup_method(self):
        """
        Set up test environment
        """
        # Create a temporary directory for test output
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_content_generation_"))
        self.output_dir = self.test_dir / "generated_content"

    def teardown_method(self):
        """
        Clean up test environment
        """
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    async def test_book_generation(self):
        """
        Test the complete book generation process
        """
        generator = BookGenerator()

        # Define test modules configuration
        modules_config = [
            {
                "name": "Test Module 1",
                "description": "A test module for content generation",
                "learning_objectives": [
                    "Understand basic concepts",
                    "Learn practical applications"
                ],
                "key_concepts": [
                    "Fundamental Principles",
                    "Core Techniques",
                    "Practical Applications"
                ],
                "num_chapters": 2
            }
        ]

        # Generate the book structure
        book_structure = await generator.generate_content_structure(modules_config)

        # Verify the structure
        assert "modules" in book_structure
        assert len(book_structure["modules"]) == 1
        assert book_structure["modules"][0]["name"] == "Test Module 1"
        assert len(book_structure["modules"][0]["chapters"]) == 2

        # Save the generated content
        success = await generator.save_generated_content(book_structure, str(self.output_dir))
        assert success

        # Verify files were created
        assert (self.output_dir / "book_structure.json").exists()
        module_dirs = list(self.output_dir.glob("module_*"))
        assert len(module_dirs) == 1

    async def test_chapter_generation(self):
        """
        Test individual chapter generation
        """
        generator = ChapterGenerator()

        # Generate a test chapter
        success = await generator.generate_and_save_chapter(
            chapter_title="Test Chapter",
            chapter_description="A test chapter for validation",
            key_concepts=["Concept 1", "Concept 2"],
            learning_objectives=["Objective 1", "Objective 2"],
            output_path=str(self.output_dir / "test_module" / "test_chapter" / "index.md")
        )

        assert success

        # Verify the file was created
        chapter_file = self.output_dir / "test_module" / "test_chapter" / "index.md"
        assert chapter_file.exists()

        # Read and verify content
        content = chapter_file.read_text()
        assert "Test Chapter" in content
        assert "Concept 1" in content

    async def test_content_validation(self):
        """
        Test content validation functionality
        """
        validator = ContentValidator()

        # Test module validation
        test_module = {
            "name": "Test Module",
            "description": "A test module",
            "learning_objectives": ["Learn something"],
            "key_concepts": ["Concept"],
            "chapters": [
                {
                    "title": "Test Chapter",
                    "description": "A test chapter",
                    "sections": [
                        {
                            "title": "Introduction",
                            "content": "This is a test section with sufficient content to meet validation requirements."
                        }
                    ]
                }
            ]
        }

        result = await validator.validate_module_content(test_module)
        assert isinstance(result, ValidationResult)
        assert result.is_valid  # Should be valid with proper content

        # Test markdown validation
        test_markdown = """---
title: Test Chapter
description: A test chapter
sidebar_position: 1
---

# Test Chapter

This is a test chapter with proper structure.

## Introduction

This section introduces the main concepts.

## Main Content

This section covers the core content.

## Summary

This chapter covered the basic concepts.
"""
        result = await validator.validate_markdown_content(test_markdown)
        assert isinstance(result, ValidationResult)
        assert result.is_valid  # Should be valid with proper markdown

    async def test_content_routing(self):
        """
        Test content routing functionality
        """
        # First generate some content to route
        generator = ContentGenerator()

        spec = {
            "title": "Test Book",
            "description": "A test book for routing",
            "modules": [
                {
                    "name": "Test Module",
                    "description": "A test module",
                    "learning_objectives": ["Learn concepts"],
                    "key_concepts": ["Test Concept"],
                    "num_chapters": 1
                }
            ]
        }

        # Generate content
        success = await generator.generate_book_from_spec(
            spec_path=None,  # We'll pass the spec directly
            output_dir=str(self.output_dir)
        )

        # Since we can't pass spec directly, let's create a temporary spec file
        spec_file = self.test_dir / "test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f)

        success = await generator.generate_book_from_spec(
            spec_path=str(spec_file),
            output_dir=str(self.output_dir)
        )

        assert success

        # Initialize content router
        router = ContentRouter(content_dir=str(self.output_dir))
        rag_service = RAGContentService(router)

        # Test content search
        results = await router.search_content("test")
        assert isinstance(results, list)

        # Test RAG content retrieval
        rag_results = await rag_service.get_relevant_content("test", top_k=3)
        assert isinstance(rag_results, list)
        assert len(rag_results) <= 3

    async def test_complete_generation_pipeline(self):
        """
        Test the complete content generation pipeline
        """
        # Initialize all components
        generator = ContentGenerator()
        validator = ContentValidator()

        # Define a comprehensive test specification
        spec = {
            "title": "AI Fundamentals",
            "description": "A comprehensive guide to AI fundamentals",
            "modules": [
                {
                    "name": "Introduction to AI",
                    "description": "Fundamental concepts of artificial intelligence",
                    "learning_objectives": [
                        "Understand basic AI concepts",
                        "Learn about different AI approaches",
                        "Explore AI applications"
                    ],
                    "key_concepts": [
                        "Machine Learning",
                        "Neural Networks",
                        "Natural Language Processing"
                    ],
                    "num_chapters": 3
                },
                {
                    "name": "Machine Learning Basics",
                    "description": "Core concepts of machine learning",
                    "learning_objectives": [
                        "Understand supervised learning",
                        "Learn about neural networks",
                        "Explore deep learning concepts"
                    ],
                    "key_concepts": [
                        "Supervised Learning",
                        "Unsupervised Learning",
                        "Reinforcement Learning"
                    ],
                    "num_chapters": 2
                }
            ]
        }

        # Create spec file
        spec_file = self.test_dir / "complete_test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        # Generate the complete book
        success = await generator.generate_book_from_spec(
            spec_path=str(spec_file),
            output_dir=str(self.output_dir)
        )

        assert success

        # Validate the generated content
        validation_results = await validator.validate_generated_content(str(self.output_dir))
        assert validation_results["valid"] or validation_results["summary"]["invalid_files"] == 0

        # Verify the structure
        assert (self.output_dir / "book_structure.json").exists()
        module_dirs = list(self.output_dir.glob("module_*"))
        assert len(module_dirs) == 2  # Should have 2 modules

        # Count total chapters
        total_chapters = 0
        for module_dir in module_dirs:
            chapter_dirs = list(module_dir.glob("chapter_*"))
            total_chapters += len(chapter_dirs)

        assert total_chapters == 5  # 3 + 2 chapters

    async def test_content_routing_with_generated_content(self):
        """
        Test content routing with generated content
        """
        # Generate test content first
        generator = ContentGenerator()

        spec = {
            "title": "Routing Test Book",
            "description": "A book for testing content routing",
            "modules": [
                {
                    "name": "Routing Test Module",
                    "description": "A module for routing tests",
                    "learning_objectives": ["Test routing"],
                    "key_concepts": ["Routing", "Content Access"],
                    "num_chapters": 1
                }
            ]
        }

        spec_file = self.test_dir / "routing_test_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f)

        success = await generator.generate_book_from_spec(
            spec_path=str(spec_file),
            output_dir=str(self.output_dir)
        )

        assert success

        # Initialize content router with generated content
        router = ContentRouter(content_dir=str(self.output_dir))

        # Test getting content by path
        content_files = list(Path(self.output_dir).rglob("*.md"))
        assert len(content_files) > 0

        first_file = content_files[0]
        relative_path = str(first_file.relative_to(self.output_dir))

        content_data = await router.get_content_by_path(relative_path)
        assert content_data is not None
        assert "content" in content_data
        assert "metadata" in content_data

        # Test content chunks
        chunks = await router.get_content_chunks(relative_path, chunk_size=500)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert "chunk_id" in chunks[0]
        assert "content" in chunks[0]

    async def run_all_tests(self):
        """
        Run all tests in the pipeline
        """
        print("Running content generation pipeline tests...")

        await self.test_book_generation()
        print("✓ Book generation test passed")

        await self.test_chapter_generation()
        print("✓ Chapter generation test passed")

        await self.test_content_validation()
        print("✓ Content validation test passed")

        await self.test_content_routing()
        print("✓ Content routing test passed")

        await self.test_complete_generation_pipeline()
        print("✓ Complete generation pipeline test passed")

        await self.test_content_routing_with_generated_content()
        print("✓ Content routing with generated content test passed")

        print("All tests passed! ✅")


async def main():
    """
    Main function to run the tests
    """
    test_instance = TestContentGenerationPipeline()

    # Setup
    test_instance.setup_method()

    try:
        await test_instance.run_all_tests()
    finally:
        # Teardown
        test_instance.teardown_method()


if __name__ == "__main__":
    asyncio.run(main())