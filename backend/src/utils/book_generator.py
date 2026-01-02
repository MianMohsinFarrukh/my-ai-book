"""
Book content generation utilities using Claude Code Router and Spec-Kit Plus
"""
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class BookGenerator:
    """
    Class to handle automatic book content generation using Claude Code Router
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the book generator with configuration

        Args:
            config_path: Path to configuration file for Claude Code Router
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration for book generation
        """
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "claude_code_router": {
                    "enabled": True,
                    "api_key": None,
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 4000,
                    "temperature": 0.7
                },
                "spec_kit_plus": {
                    "templates_dir": "templates/modules",
                    "output_dir": "generated_content",
                    "module_structure": {
                        "title": "Module Title",
                        "description": "Module Description",
                        "chapters": [],
                        "learning_objectives": [],
                        "key_concepts": []
                    }
                }
            }

    async def generate_module(
        self,
        module_name: str,
        description: str,
        learning_objectives: List[str],
        key_concepts: List[str],
        num_chapters: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a complete module with chapters using Claude Code Router

        Args:
            module_name: Name of the module to generate
            description: Description of the module
            learning_objectives: List of learning objectives
            key_concepts: List of key concepts to cover
            num_chapters: Number of chapters to generate

        Returns:
            Dictionary containing generated module structure
        """
        logger.info(f"Generating module: {module_name}")

        # This would integrate with Claude Code Router in a real implementation
        # For now, we'll simulate the generation process

        module_structure = {
            "name": module_name,
            "description": description,
            "learning_objectives": learning_objectives,
            "key_concepts": key_concepts,
            "chapters": []
        }

        # Generate chapters
        for i in range(1, num_chapters + 1):
            chapter = await self._generate_chapter(
                module_name=module_name,
                chapter_num=i,
                key_concepts=key_concepts
            )
            module_structure["chapters"].append(chapter)

        return module_structure

    async def _generate_chapter(
        self,
        module_name: str,
        chapter_num: int,
        key_concepts: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a single chapter within a module

        Args:
            module_name: Name of the parent module
            chapter_num: Chapter number
            key_concepts: Key concepts to include in the chapter

        Returns:
            Dictionary containing chapter structure
        """
        logger.info(f"Generating chapter {chapter_num} for module {module_name}")

        # In a real implementation, this would call Claude Code Router
        # to generate the actual content based on the key concepts

        chapter = {
            "title": f"Chapter {chapter_num}: {key_concepts[chapter_num % len(key_concepts)] if key_concepts else 'Topic'}",
            "description": f"Chapter {chapter_num} of {module_name} covering key concepts",
            "sections": [
                {
                    "title": "Introduction",
                    "content": f"Introduction to the concepts covered in Chapter {chapter_num}",
                    "learning_objectives": []
                },
                {
                    "title": "Main Content",
                    "content": f"Detailed explanation of key concepts: {', '.join(key_concepts[:2])}",
                    "learning_objectives": []
                },
                {
                    "title": "Summary",
                    "content": f"Summary of Chapter {chapter_num} concepts and their applications",
                    "learning_objectives": []
                }
            ],
            "exercises": [
                {
                    "type": "concept_check",
                    "question": f"How does the concept of {key_concepts[chapter_num % len(key_concepts)] if key_concepts else 'this topic'} apply?",
                    "answer": "This concept is fundamental to understanding the module."
                }
            ]
        }

        return chapter

    async def generate_content_structure(
        self,
        modules_config: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate complete book structure with multiple modules and chapters

        Args:
            modules_config: List of module configurations to generate

        Returns:
            Dictionary containing complete book structure
        """
        logger.info(f"Generating content structure for {len(modules_config)} modules")

        book_structure = {
            "title": "Generated AI Book",
            "description": "Book generated using Claude Code Router and Spec-Kit Plus",
            "modules": []
        }

        for module_config in modules_config:
            module = await self.generate_module(
                module_name=module_config.get("name", "Untitled Module"),
                description=module_config.get("description", ""),
                learning_objectives=module_config.get("learning_objectives", []),
                key_concepts=module_config.get("key_concepts", []),
                num_chapters=module_config.get("num_chapters", 3)
            )
            book_structure["modules"].append(module)

        return book_structure

    async def save_generated_content(
        self,
        content: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Save generated content to the specified output path in Docusaurus format

        Args:
            content: Generated content structure
            output_path: Path to save the content

        Returns:
            True if successful, False otherwise
        """
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the complete book structure
            with open(output_dir / "book_structure.json", "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

            # Generate Docusaurus-compatible markdown files
            await self._generate_docusaurus_content(content, output_dir)

            logger.info(f"Generated content saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving generated content: {e}")
            return False

    async def _generate_docusaurus_content(
        self,
        content: Dict[str, Any],
        output_dir: Path
    ) -> None:
        """
        Generate Docusaurus-compatible markdown files from the content structure

        Args:
            content: Generated content structure
            output_dir: Output directory for markdown files
        """
        for module_idx, module in enumerate(content["modules"]):
            module_dir = output_dir / f"module_{module_idx + 1:02d}_{module['name'].lower().replace(' ', '_')}"
            module_dir.mkdir(exist_ok=True)

            # Create module index file
            module_index_content = f"""---
sidebar_position: {module_idx + 1}
---

# {module['name']}

{module['description']}

## Learning Objectives

{chr(10).join([f"- {obj}" for obj in module['learning_objectives']])}

## Key Concepts

{chr(10).join([f"- {concept}" for concept in module['key_concepts']])}
"""

            with open(module_dir / "index.md", "w", encoding="utf-8") as f:
                f.write(module_index_content)

            # Create chapter files
            for chapter_idx, chapter in enumerate(module["chapters"]):
                chapter_dir = module_dir / f"chapter_{chapter_idx + 1:02d}_{chapter['title'].lower().replace(' ', '_').replace(':', '').replace('?', '').replace(',', '')}"
                chapter_dir.mkdir(exist_ok=True)

                chapter_content = f"""---
sidebar_position: {chapter_idx + 1}
---

# {chapter['title']}

{chapter['description']}

"""

                for section in chapter["sections"]:
                    chapter_content += f"""
## {section['title']}

{section['content']}

"""

                # Add exercises section
                if chapter["exercises"]:
                    chapter_content += "\n## Exercises\n\n"
                    for exercise_idx, exercise in enumerate(chapter["exercises"], 1):
                        chapter_content += f"""
**Exercise {exercise_idx}: {exercise['type'].title()}**

{exercise['question']}

"""

                with open(chapter_dir / "index.md", "w", encoding="utf-8") as f:
                    f.write(chapter_content)


# Example usage
async def main():
    """
    Example of how to use the BookGenerator
    """
    generator = BookGenerator()

    # Define modules to generate
    modules_config = [
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
                "Natural Language Processing",
                "Computer Vision"
            ],
            "num_chapters": 4
        },
        {
            "name": "Machine Learning Fundamentals",
            "description": "Core concepts of machine learning",
            "learning_objectives": [
                "Understand supervised learning",
                "Learn about neural networks",
                "Explore deep learning concepts"
            ],
            "key_concepts": [
                "Supervised Learning",
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Model Evaluation"
            ],
            "num_chapters": 3
        }
    ]

    # Generate the complete book structure
    book_structure = await generator.generate_content_structure(modules_config)

    # Save the generated content
    success = await generator.save_generated_content(book_structure, "generated_book")

    if success:
        print("Book content generated successfully!")
    else:
        print("Failed to generate book content.")


if __name__ == "__main__":
    asyncio.run(main())