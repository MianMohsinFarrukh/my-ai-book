"""
Chapter generation utilities using Claude integration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import re
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class ChapterGenerator:
    """
    Class to handle automatic chapter generation with Claude integration
    """

    def __init__(self, templates_dir: str = "templates/modules"):
        """
        Initialize the chapter generator with templates

        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Load configuration
        config_path = self.templates_dir / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "chapter_template": {
                    "path": "chapter_template.md",
                    "required_fields": [
                        "CHAPTER_TITLE",
                        "CHAPTER_DESCRIPTION",
                        "LEARNING_OBJECTIVES",
                        "INTRODUCTION",
                        "SECTION_TITLE_1",
                        "SECTION_CONTENT_1",
                        "CHAPTER_SUMMARY"
                    ]
                }
            }

    async def generate_chapter_content(
        self,
        chapter_title: str,
        chapter_description: str,
        key_concepts: List[str],
        learning_objectives: List[str],
        module_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete chapter content using Claude integration

        Args:
            chapter_title: Title of the chapter
            chapter_description: Description of the chapter
            key_concepts: Key concepts to cover in the chapter
            learning_objectives: Learning objectives for the chapter
            module_context: Context from the parent module

        Returns:
            Dictionary containing generated chapter content
        """
        logger.info(f"Generating chapter content: {chapter_title}")

        # Simulate Claude integration to generate content
        # In a real implementation, this would call the Claude API
        chapter_content = await self._simulate_claude_generation(
            chapter_title,
            chapter_description,
            key_concepts,
            learning_objectives,
            module_context
        )

        return chapter_content

    async def _simulate_claude_generation(
        self,
        chapter_title: str,
        chapter_description: str,
        key_concepts: List[str],
        learning_objectives: List[str],
        module_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simulate Claude API call to generate chapter content
        In a real implementation, this would call the actual Claude API

        Args:
            chapter_title: Title of the chapter
            chapter_description: Description of the chapter
            key_concepts: Key concepts to cover
            learning_objectives: Learning objectives
            module_context: Module context

        Returns:
            Generated chapter content as dictionary
        """
        # This is a simulation - in real implementation, this would call Claude API
        # For now, we'll generate content based on the provided parameters

        # Generate sections based on key concepts
        sections = []
        for i, concept in enumerate(key_concepts[:3]):  # Limit to 3 main sections
            section_title = f"{concept} Explained"
            section_content = f"This section covers the concept of {concept} in detail, explaining its importance, applications, and implementation. We'll explore how {concept} fits into the broader context of the chapter topic."

            sections.append({
                "title": section_title,
                "content": section_content,
                "type": "explanation"
            })

        # Add practical example
        practical_example = f"In this practical example, we'll demonstrate how to apply the concepts of {', '.join(key_concepts[:2])} in a real-world scenario. This will help reinforce the learning objectives and provide hands-on experience."

        # Generate exercises
        exercises = []
        for i, obj in enumerate(learning_objectives[:2]):
            exercise = {
                "type": "application",
                "question": f"How would you apply the concepts learned in this chapter to achieve: {obj}?",
                "answer": f"To achieve '{obj}', you would need to understand and implement the concepts covered in this chapter, particularly focusing on {key_concepts[i % len(key_concepts)] if key_concepts else 'the main concepts'}."
            }
            exercises.append(exercise)

        # Generate key takeaways
        key_takeaways = [
            f"Key concept {concept} is fundamental to understanding the chapter topic",
            f"Learning objective '{obj}' has been addressed through practical examples",
            f"The relationship between different concepts has been demonstrated"
        ] for concept in key_concepts[:2] for obj in learning_objectives[:1]

        # Flatten the list
        key_takeaways = [item for sublist in key_takeaways for item in sublist][:3]

        chapter_content = {
            "title": chapter_title,
            "description": chapter_description,
            "learning_objectives": learning_objectives,
            "introduction": f"Welcome to {chapter_title}. In this chapter, we'll explore the fundamental concepts of {', '.join(key_concepts[:2])} and how they relate to the broader topic. By the end of this chapter, you should have a solid understanding of these concepts and be able to apply them in practical scenarios.",
            "sections": sections,
            "practical_example": practical_example,
            "summary": f"In this chapter, we've covered the key concepts of {', '.join(key_concepts[:2])} and how they relate to the learning objectives. We've provided practical examples and exercises to reinforce your understanding. The next chapter will build on these concepts.",
            "exercises": exercises,
            "key_takeaways": key_takeaways,
            "references": [
                {
                    "title": "Additional Reading on " + key_concepts[0] if key_concepts else "Topic",
                    "url": f"https://example.com/{key_concepts[0].lower().replace(' ', '-')}" if key_concepts else "https://example.com/reference"
                }
            ]
        }

        return chapter_content

    async def render_chapter_markdown(
        self,
        chapter_data: Dict[str, Any]
    ) -> str:
        """
        Render chapter data into Docusaurus-compatible markdown using Jinja2 template

        Args:
            chapter_data: Dictionary containing chapter data

        Returns:
            Rendered markdown string
        """
        try:
            # Load the chapter template
            template = self.env.get_template(self.config["chapter_template"]["path"])

            # Prepare template context
            template_context = {
                "CHAPTER_TITLE": chapter_data.get("title", "Untitled Chapter"),
                "CHAPTER_DESCRIPTION": chapter_data.get("description", ""),
                "LEARNING_OBJECTIVES": chapter_data.get("learning_objectives", []),
                "INTRODUCTION": chapter_data.get("introduction", ""),
                "PRACTICAL_EXAMPLE": chapter_data.get("practical_example", ""),
                "CHAPTER_SUMMARY": chapter_data.get("summary", ""),
                "EXERCISES": chapter_data.get("exercises", []),
                "KEY_TAKEAWAYS": chapter_data.get("key_takeaways", []),
                "REFERENCES": chapter_data.get("references", [])
            }

            # Add sections to template context
            sections = chapter_data.get("sections", [])
            for i, section in enumerate(sections):
                template_context[f"SECTION_TITLE_{i+1}"] = section.get("title", f"Section {i+1}")
                template_context[f"SECTION_CONTENT_{i+1}"] = section.get("content", "")
                # If section has code, add it
                if "code" in section:
                    template_context[f"SECTION_CODE_{i+1}"] = section["code"]

            # Set default values for missing sections
            for i in range(len(sections) + 1, 4):  # Up to 3 sections
                template_context[f"SECTION_TITLE_{i}"] = ""
                template_context[f"SECTION_CONTENT_{i}"] = ""
                template_context[f"SECTION_CODE_{i}"] = ""

            # Set default code language
            template_context["CODE_LANGUAGE"] = "python"

            # Render the template
            rendered_markdown = template.render(**template_context)

            return rendered_markdown

        except Exception as e:
            logger.error(f"Error rendering chapter markdown: {e}")
            raise

    async def generate_and_save_chapter(
        self,
        chapter_title: str,
        chapter_description: str,
        key_concepts: List[str],
        learning_objectives: List[str],
        output_path: str,
        module_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Generate a complete chapter and save it as markdown

        Args:
            chapter_title: Title of the chapter
            chapter_description: Description of the chapter
            key_concepts: Key concepts to cover
            learning_objectives: Learning objectives
            output_path: Path to save the generated chapter
            module_context: Context from parent module

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate chapter content
            chapter_data = await self.generate_chapter_content(
                chapter_title,
                chapter_description,
                key_concepts,
                learning_objectives,
                module_context
            )

            # Render to markdown
            markdown_content = await self.render_chapter_markdown(chapter_data)

            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Chapter saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating and saving chapter: {e}")
            return False

    async def batch_generate_chapters(
        self,
        chapters_config: List[Dict[str, Any]],
        output_dir: str
    ) -> List[Tuple[str, bool]]:
        """
        Generate multiple chapters in batch

        Args:
            chapters_config: List of chapter configurations
            output_dir: Directory to save generated chapters

        Returns:
            List of tuples with (chapter_title, success_status)
        """
        results = []

        for i, config in enumerate(chapters_config):
            chapter_title = config.get("title", f"Chapter {i+1}")
            output_path = f"{output_dir}/chapter_{i+1:02d}_{chapter_title.lower().replace(' ', '_').replace(':', '').replace('?', '').replace(',', '')}/index.md"

            success = await self.generate_and_save_chapter(
                chapter_title=config.get("title", f"Chapter {i+1}"),
                chapter_description=config.get("description", ""),
                key_concepts=config.get("key_concepts", []),
                learning_objectives=config.get("learning_objectives", []),
                output_path=output_path,
                module_context=config.get("module_context")
            )

            results.append((chapter_title, success))

        return results


# Example usage
async def main():
    """
    Example of how to use the ChapterGenerator
    """
    generator = ChapterGenerator()

    # Example chapter configuration
    chapter_config = {
        "title": "Introduction to Neural Networks",
        "description": "Learn the fundamentals of neural networks and their applications",
        "key_concepts": [
            "Neurons and Activation Functions",
            "Forward and Backward Propagation",
            "Loss Functions and Optimization"
        ],
        "learning_objectives": [
            "Understand the basic structure of neural networks",
            "Learn how neural networks learn from data",
            "Explore common applications of neural networks"
        ]
    }

    # Generate and save the chapter
    success = await generator.generate_and_save_chapter(
        chapter_title=chapter_config["title"],
        chapter_description=chapter_config["description"],
        key_concepts=chapter_config["key_concepts"],
        learning_objectives=chapter_config["learning_objectives"],
        output_path="generated_content/test_chapter/index.md"
    )

    if success:
        print("Chapter generated successfully!")
    else:
        print("Failed to generate chapter.")


if __name__ == "__main__":
    asyncio.run(main())