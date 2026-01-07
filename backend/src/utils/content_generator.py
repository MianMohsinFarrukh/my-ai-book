"""
Content structure generation script that orchestrates book generation
using Claude Code Router and Spec-Kit Plus
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml
from datetime import datetime

from .book_generator import BookGenerator
from .chapter_generator import ChapterGenerator

logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Main class to orchestrate content generation using multiple generators
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the content generator

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.book_generator = BookGenerator(config_path)
        self.chapter_generator = ChapterGenerator()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration for content generation
        """
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml') else json.load(f)
        else:
            # Default configuration
            return {
                "content_generation": {
                    "output_dir": "generated_content",
                    "docusaurus_compatible": True,
                    "include_exercises": True,
                    "validate_content": True
                },
                "claude_integration": {
                    "enabled": True,
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                "generation_limits": {
                    "max_modules": 10,
                    "max_chapters_per_module": 10,
                    "max_sections_per_chapter": 10
                }
            }

    async def generate_book_from_spec(
        self,
        spec_path: str,
        output_dir: Optional[str] = None
    ) -> bool:
        """
        Generate complete book content from a specification file

        Args:
            spec_path: Path to specification file (JSON/YAML)
            output_dir: Output directory for generated content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the specification
            spec = await self._load_specification(spec_path)

            if output_dir is None:
                output_dir = self.config["content_generation"]["output_dir"]

            logger.info(f"Generating book content from specification: {spec_path}")

            # Generate the book structure
            book_structure = await self.book_generator.generate_content_structure(
                spec.get("modules", [])
            )

            # Save the generated content
            success = await self.book_generator.save_generated_content(
                book_structure,
                output_dir
            )

            if success:
                logger.info("Book content generated successfully!")

                # Generate additional content if needed
                await self._generate_additional_content(book_structure, output_dir)

                return True
            else:
                logger.error("Failed to generate book content")
                return False

        except Exception as e:
            logger.error(f"Error generating book from spec: {e}")
            return False

    async def _load_specification(self, spec_path: str) -> Dict[str, Any]:
        """
        Load specification from JSON or YAML file

        Args:
            spec_path: Path to specification file

        Returns:
            Specification as dictionary
        """
        path = Path(spec_path)

        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)

    async def _generate_additional_content(
        self,
        book_structure: Dict[str, Any],
        output_dir: str
    ) -> None:
        """
        Generate additional content like exercises, quizzes, etc.

        Args:
            book_structure: Generated book structure
            output_dir: Output directory
        """
        logger.info("Generating additional content...")

        # Generate exercises for each chapter
        for module_idx, module in enumerate(book_structure["modules"]):
            for chapter_idx, chapter in enumerate(module["chapters"]):
                # Add more detailed exercises
                detailed_exercises = await self._generate_detailed_exercises(
                    chapter,
                    f"{output_dir}/module_{module_idx + 1:02d}_{module['name'].lower().replace(' ', '_')}/chapter_{chapter_idx + 1:02d}_{chapter['title'].lower().replace(' ', '_').replace(':', '').replace('?', '').replace(',', '')}"
                )

                # Update the chapter with detailed exercises
                chapter["detailed_exercises"] = detailed_exercises

    async def _generate_detailed_exercises(
        self,
        chapter: Dict[str, Any],
        chapter_dir: str
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed exercises for a chapter

        Args:
            chapter: Chapter data
            chapter_dir: Directory for the chapter

        Returns:
            List of detailed exercises
        """
        exercises = []

        # Create a practice notebook if code examples exist
        if any('code' in section for section in chapter.get("sections", [])):
            notebook_content = self._generate_practice_notebook(chapter)

            # Save the notebook
            notebook_path = f"{chapter_dir}/practice_notebook.ipynb"
            with open(notebook_path, 'w', encoding='utf-8') as f:
                f.write(notebook_content)

        # Generate quiz questions
        quiz_questions = await self._generate_quiz_questions(chapter)
        exercises.extend(quiz_questions)

        return exercises

    def _generate_practice_notebook(self, chapter: Dict[str, Any]) -> str:
        """
        Generate a practice Jupyter notebook for the chapter

        Args:
            chapter: Chapter data

        Returns:
            Notebook content as string
        """
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# Practice: {chapter['title']}\n\n",
                        f"Complete the exercises below to reinforce your understanding of {chapter['title']}."
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        # Add code cells based on chapter sections
        for section in chapter.get("sections", []):
            if "code" in section:
                notebook["cells"].append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [section["code"]]
                })

                # Add exercise cell
                notebook["cells"].append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["**Exercise**: Modify the code above to implement the concept in a different way."]
                })

        return json.dumps(notebook, indent=2)

    async def _generate_quiz_questions(self, chapter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for the chapter

        Args:
            chapter: Chapter data

        Returns:
            List of quiz questions
        """
        quiz_questions = []

        # Generate questions based on key concepts
        key_concepts = chapter.get("sections", [])
        for i, section in enumerate(key_concepts[:3]):
            question = {
                "type": "multiple_choice",
                "question": f"What is the main concept covered in '{section.get('title', 'Section')}'?",
                "options": [
                    section.get('content', '')[:50] + "...",
                    "Another concept",
                    "A different approach",
                    "None of the above"
                ],
                "correct_answer": 0,
                "explanation": f"This question tests understanding of {section.get('title', 'the main concept')}"
            }
            quiz_questions.append(question)

        return quiz_questions

    async def generate_module_structure(
        self,
        module_name: str,
        module_spec: Dict[str, Any],
        output_dir: str
    ) -> bool:
        """
        Generate a single module structure

        Args:
            module_name: Name of the module
            module_spec: Module specification
            output_dir: Output directory

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Generating module: {module_name}")

            # Generate the module
            module = await self.book_generator.generate_module(
                module_name=module_spec.get("name", module_name),
                description=module_spec.get("description", ""),
                learning_objectives=module_spec.get("learning_objectives", []),
                key_concepts=module_spec.get("key_concepts", []),
                num_chapters=module_spec.get("num_chapters", 3)
            )

            # Create book structure with just this module
            book_structure = {
                "title": f"{module_name} Module",
                "description": f"Module {module_name} generated on {datetime.now().isoformat()}",
                "modules": [module]
            }

            # Save the module content
            success = await self.book_generator.save_generated_content(
                book_structure,
                f"{output_dir}/{module_name.lower().replace(' ', '_')}"
            )

            return success

        except Exception as e:
            logger.error(f"Error generating module {module_name}: {e}")
            return False

    async def validate_generated_content(
        self,
        content_dir: str
    ) -> Dict[str, Any]:
        """
        Validate the generated content for completeness and correctness

        Args:
            content_dir: Directory containing generated content

        Returns:
            Validation results
        """
        results = {
            "total_files": 0,
            "markdown_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "issues": []
        }

        content_path = Path(content_dir)

        if not content_path.exists():
            results["issues"].append(f"Content directory does not exist: {content_dir}")
            return results

        # Walk through the directory
        for file_path in content_path.rglob("*"):
            if file_path.is_file():
                results["total_files"] += 1

                if file_path.suffix.lower() == '.md':
                    results["markdown_files"] += 1

                    # Validate markdown file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Basic validation checks
                        issues = []

                        # Check for frontmatter
                        if not content.strip().startswith('---'):
                            issues.append("Missing frontmatter")

                        # Check for required sections
                        required_sections = ['#', '## Learning Objectives', '## Summary']
                        for section in required_sections:
                            if section not in content:
                                issues.append(f"Missing section: {section}")

                        if issues:
                            results["invalid_files"] += 1
                            results["issues"].append({
                                "file": str(file_path),
                                "issues": issues
                            })
                        else:
                            results["valid_files"] += 1

                    except Exception as e:
                        results["invalid_files"] += 1
                        results["issues"].append({
                            "file": str(file_path),
                            "error": str(e)
                        })

        return results

    async def create_generation_report(
        self,
        validation_results: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Create a generation report with validation results

        Args:
            validation_results: Results from content validation
            output_path: Path to save the report

        Returns:
            True if successful, False otherwise
        """
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "validation_results": validation_results,
                "summary": {
                    "total_files": validation_results["total_files"],
                    "valid_files": validation_results["valid_files"],
                    "invalid_files": validation_results["invalid_files"],
                    "validity_percentage": (
                        validation_results["valid_files"] / validation_results["total_files"] * 100
                        if validation_results["total_files"] > 0 else 0
                    )
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Generation report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating generation report: {e}")
            return False


# Example usage
async def main():
    """
    Example of how to use the ContentGenerator
    """
    generator = ContentGenerator()

    # Example specification
    spec = {
        "title": "AI Fundamentals",
        "description": "A comprehensive book on artificial intelligence fundamentals",
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
            }
        ]
    }

    # Save spec to file for testing
    with open("test_spec.json", "w") as f:
        json.dump(spec, f, indent=2)

    # Generate the book
    success = await generator.generate_book_from_spec("test_spec.json", "generated_book")

    if success:
        print("Book generated successfully!")

        # Validate the generated content
        validation_results = await generator.validate_generated_content("generated_book")
        print(f"Validation results: {validation_results}")

        # Create a report
        await generator.create_generation_report(validation_results, "generation_report.json")
    else:
        print("Failed to generate book.")


if __name__ == "__main__":
    asyncio.run(main())