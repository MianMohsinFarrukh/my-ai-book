"""
Content validation utilities for generated modules and chapters
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import re
from datetime import datetime
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """
    Data class to hold validation results
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    validation_time: float

class ContentValidator:
    """
    Service to validate generated content for quality and correctness
    """

    def __init__(self):
        """
        Initialize the content validator
        """
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """
        Load validation rules for content validation

        Returns:
            Dictionary containing validation rules
        """
        return {
            "required_sections": [
                "title",
                "learning_objectives",
                "summary"
            ],
            "content_quality": {
                "min_word_count": 200,
                "max_word_count": 5000,
                "min_paragraph_length": 20,
                "max_paragraph_length": 500
            },
            "formatting": {
                "required_frontmatter": ["title", "description", "sidebar_position"],
                "forbidden_patterns": [
                    r"\b(assumption|presumably|maybe|perhaps)\b",  # Avoid uncertain language
                    r"\b(FIXME|TODO|XXX)\b",  # Avoid placeholder text
                    r"^\s*#+\s*$",  # Empty headings
                    r"\n{3,}"  # Multiple consecutive blank lines
                ],
                "required_patterns": [
                    r"\b(understand|learn|apply|demonstrate)\b"  # Action-oriented language
                ]
            },
            "structure": {
                "min_sections": 2,
                "max_sections": 10,
                "min_exercises": 0,
                "max_exercises": 10
            },
            "accuracy": {
                "fact_check_required": True,
                "source_citations_required": False
            }
        }

    async def validate_module_content(
        self,
        module_data: Dict[str, Any],
        content_path: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate module content

        Args:
            module_data: Module data to validate
            content_path: Optional path to content file

        Returns:
            Validation result
        """
        start_time = datetime.now()

        errors = []
        warnings = []
        suggestions = []

        # Validate required fields
        required_fields = ["name", "description", "learning_objectives", "key_concepts", "chapters"]
        for field in required_fields:
            if field not in module_data or not module_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate learning objectives
        if "learning_objectives" in module_data:
            objectives = module_data["learning_objectives"]
            if not isinstance(objectives, list) or len(objectives) == 0:
                errors.append("Learning objectives must be a non-empty list")
            else:
                for i, obj in enumerate(objectives):
                    if not isinstance(obj, str) or len(obj.strip()) == 0:
                        errors.append(f"Learning objective {i+1} must be a non-empty string")

        # Validate key concepts
        if "key_concepts" in module_data:
            concepts = module_data["key_concepts"]
            if not isinstance(concepts, list) or len(concepts) == 0:
                errors.append("Key concepts must be a non-empty list")
            else:
                for i, concept in enumerate(concepts):
                    if not isinstance(concept, str) or len(concept.strip()) == 0:
                        errors.append(f"Key concept {i+1} must be a non-empty string")

        # Validate chapters
        if "chapters" in module_data:
            chapters = module_data["chapters"]
            if not isinstance(chapters, list) or len(chapters) == 0:
                errors.append("Chapters must be a non-empty list")
            else:
                for i, chapter in enumerate(chapters):
                    chapter_result = await self.validate_chapter_content(chapter, f"{content_path}/chapter_{i+1}" if content_path else None)
                    errors.extend([f"Chapter {i+1}: {error}" for error in chapter_result.errors])
                    warnings.extend([f"Chapter {i+1}: {warning}" for warning in chapter_result.warnings])
                    suggestions.extend([f"Chapter {i+1}: {suggestion}" for suggestion in chapter_result.suggestions])

        # Check for reasonable number of chapters
        if "chapters" in module_data and len(module_data["chapters"]) > 20:
            warnings.append("Module has more than 20 chapters, consider breaking it into multiple modules")

        validation_time = (datetime.now() - start_time).total_seconds()

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_time=validation_time
        )

    async def validate_chapter_content(
        self,
        chapter_data: Dict[str, Any],
        content_path: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate chapter content

        Args:
            chapter_data: Chapter data to validate
            content_path: Optional path to content file

        Returns:
            Validation result
        """
        start_time = datetime.now()

        errors = []
        warnings = []
        suggestions = []

        # Validate required fields for chapter
        required_fields = ["title", "description", "sections"]
        for field in required_fields:
            if field not in chapter_data or not chapter_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate title
        if "title" in chapter_data:
            title = chapter_data["title"]
            if not isinstance(title, str) or len(title.strip()) == 0:
                errors.append("Chapter title must be a non-empty string")
            elif len(title) > 100:
                warnings.append("Chapter title is very long (over 100 characters)")

        # Validate description
        if "description" in chapter_data:
            description = chapter_data["description"]
            if not isinstance(description, str) or len(description.strip()) == 0:
                errors.append("Chapter description must be a non-empty string")
            elif len(description) < 20:
                warnings.append("Chapter description is very short (less than 20 characters)")

        # Validate sections
        if "sections" in chapter_data:
            sections = chapter_data["sections"]
            if not isinstance(sections, list) or len(sections) == 0:
                errors.append("Sections must be a non-empty list")
            elif len(sections) < 2:
                warnings.append("Chapter has fewer than 2 sections, consider adding more for better structure")
            else:
                total_content_length = 0
                for i, section in enumerate(sections):
                    section_errors, section_warnings, section_suggestions = self._validate_section(section, i)
                    errors.extend(section_errors)
                    warnings.extend(section_warnings)
                    suggestions.extend(section_suggestions)

                    if "content" in section:
                        total_content_length += len(section["content"])

                # Validate total content length
                if total_content_length < self.validation_rules["content_quality"]["min_word_count"] * 5:  # Rough char estimate
                    warnings.append(f"Chapter content seems too short (total {total_content_length} characters)")
                elif total_content_length > self.validation_rules["content_quality"]["max_word_count"] * 5:
                    warnings.append(f"Chapter content seems too long (total {total_content_length} characters)")

        # Validate exercises if present
        if "exercises" in chapter_data:
            exercises = chapter_data["exercises"]
            if isinstance(exercises, list):
                for i, exercise in enumerate(exercises):
                    ex_errors, ex_warnings, ex_suggestions = self._validate_exercise(exercise, i)
                    errors.extend(ex_errors)
                    warnings.extend(ex_warnings)
                    suggestions.extend(ex_suggestions)

        # Validate learning objectives if present
        if "learning_objectives" in chapter_data:
            objectives = chapter_data["learning_objectives"]
            if isinstance(objectives, list):
                for i, obj in enumerate(objectives):
                    if not isinstance(obj, str) or len(obj.strip()) == 0:
                        errors.append(f"Learning objective {i+1} must be a non-empty string")

        validation_time = (datetime.now() - start_time).total_seconds()

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_time=validation_time
        )

    def _validate_section(self, section: Dict[str, Any], index: int) -> Tuple[List[str], List[str], List[str]]:
        """
        Validate a single section

        Args:
            section: Section data
            index: Section index for error reporting

        Returns:
            Tuple of (errors, warnings, suggestions)
        """
        errors = []
        warnings = []
        suggestions = []

        # Check required fields
        if "title" not in section or not section["title"]:
            errors.append(f"Section {index+1} missing title")
        if "content" not in section or not section["content"]:
            errors.append(f"Section {index+1} missing content")

        # Validate content quality
        if "content" in section:
            content = section["content"]
            word_count = len(content.split())

            if word_count < self.validation_rules["content_quality"]["min_word_count"]:
                warnings.append(f"Section {index+1} content is very short ({word_count} words)")

            # Check for proper paragraph structure
            paragraphs = content.split('\n\n')
            for i, para in enumerate(paragraphs):
                para_len = len(para.strip())
                if para_len == 0:
                    continue  # Skip empty paragraphs
                elif para_len < self.validation_rules["content_quality"]["min_paragraph_length"]:
                    warnings.append(f"Section {index+1} paragraph {i+1} is very short ({para_len} chars)")
                elif para_len > self.validation_rules["content_quality"]["max_paragraph_length"]:
                    warnings.append(f"Section {index+1} paragraph {i+1} is very long ({para_len} chars), consider breaking it up")

            # Check for forbidden patterns
            for pattern in self.validation_rules["formatting"]["forbidden_patterns"]:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"Section {index+1} contains forbidden pattern: {pattern}")

        # Validate title
        if "title" in section:
            title = section["title"]
            if len(title) > 100:
                warnings.append(f"Section {index+1} title is very long (over 100 characters)")

        return errors, warnings, suggestions

    def _validate_exercise(self, exercise: Dict[str, Any], index: int) -> Tuple[List[str], List[str], List[str]]:
        """
        Validate a single exercise

        Args:
            exercise: Exercise data
            index: Exercise index for error reporting

        Returns:
            Tuple of (errors, warnings, suggestions)
        """
        errors = []
        warnings = []
        suggestions = []

        # Check required fields
        if "question" not in exercise or not exercise["question"]:
            errors.append(f"Exercise {index+1} missing question")

        # Validate question
        if "question" in exercise:
            question = exercise["question"]
            if len(question) < 10:
                warnings.append(f"Exercise {index+1} question is very short")
            elif len(question) > 500:
                warnings.append(f"Exercise {index+1} question is very long")

        # Validate answer if present
        if "answer" in exercise:
            answer = exercise["answer"]
            if len(answer) < 5:
                warnings.append(f"Exercise {index+1} answer is very short")

        # Validate type
        if "type" in exercise:
            valid_types = ["multiple_choice", "short_answer", "application", "concept_check"]
            ex_type = exercise["type"]
            if ex_type not in valid_types:
                suggestions.append(f"Exercise {index+1} type '{ex_type}' not in recommended types: {valid_types}")

        return errors, warnings, suggestions

    async def validate_markdown_content(
        self,
        markdown_content: str,
        file_path: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate markdown content structure and formatting

        Args:
            markdown_content: Raw markdown content
            file_path: Optional file path for context

        Returns:
            Validation result
        """
        start_time = datetime.now()

        errors = []
        warnings = []
        suggestions = []

        # Check for frontmatter
        lines = markdown_content.split('\n')
        has_frontmatter = False
        frontmatter_end = -1

        if len(lines) > 0 and lines[0].strip() == '---':
            has_frontmatter = True
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

        if not has_frontmatter:
            errors.append("Missing frontmatter (YAML header between ---)")
        else:
            # Parse frontmatter
            frontmatter_lines = lines[1:frontmatter_end]
            frontmatter_content = '\n'.join(frontmatter_lines)

            try:
                # Basic validation of frontmatter structure
                frontmatter_pairs = {}
                for line in frontmatter_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter_pairs[key.strip()] = value.strip().strip('"\'')

                # Check for required frontmatter fields
                required_fields = self.validation_rules["formatting"]["required_frontmatter"]
                for field in required_fields:
                    if field not in frontmatter_pairs:
                        errors.append(f"Missing required frontmatter field: {field}")

            except Exception as e:
                errors.append(f"Error parsing frontmatter: {str(e)}")

        # Check for main title
        title_found = False
        for line in lines:
            if line.strip().startswith('# ') and not line.strip().startswith('##'):
                title_found = True
                break

        if not title_found:
            errors.append("No main title (H1) found in content")

        # Check for forbidden patterns
        for pattern in self.validation_rules["formatting"]["forbidden_patterns"]:
            if re.search(pattern, markdown_content, re.IGNORECASE | re.MULTILINE):
                errors.append(f"Content contains forbidden pattern: {pattern}")

        # Check for required patterns
        has_required_patterns = False
        for pattern in self.validation_rules["formatting"]["required_patterns"]:
            if re.search(pattern, markdown_content, re.IGNORECASE):
                has_required_patterns = True
                break

        if not has_required_patterns:
            warnings.append("Content doesn't contain recommended action-oriented language")

        # Check content length
        content_without_frontmatter = '\n'.join(lines[frontmatter_end + 1:]) if has_frontmatter else markdown_content
        word_count = len(content_without_frontmatter.split())

        if word_count < self.validation_rules["content_quality"]["min_word_count"]:
            warnings.append(f"Content is very short ({word_count} words)")
        elif word_count > self.validation_rules["content_quality"]["max_word_count"]:
            warnings.append(f"Content is very long ({word_count} words)")

        validation_time = (datetime.now() - start_time).total_seconds()

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_time=validation_time
        )

    async def validate_generated_content(
        self,
        content_dir: str
    ) -> Dict[str, Any]:
        """
        Validate all content in a directory

        Args:
            content_dir: Directory containing generated content

        Returns:
            Comprehensive validation report
        """
        content_path = Path(content_dir)

        if not content_path.exists():
            return {
                "valid": False,
                "error": f"Content directory does not exist: {content_dir}",
                "summary": {"total_files": 0, "valid_files": 0, "invalid_files": 0}
            }

        validation_results = {
            "valid": True,
            "summary": {
                "total_files": 0,
                "markdown_files": 0,
                "valid_files": 0,
                "invalid_files": 0,
                "total_errors": 0,
                "total_warnings": 0
            },
            "details": [],
            "timestamp": datetime.now().isoformat()
        }

        for md_file in content_path.rglob("*.md"):
            validation_results["summary"]["total_files"] += 1

            if md_file.suffix.lower() == '.md':
                validation_results["summary"]["markdown_files"] += 1

                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    result = await self.validate_markdown_content(content, str(md_file))

                    file_result = {
                        "file": str(md_file.relative_to(content_path)),
                        "valid": result.is_valid,
                        "errors": result.errors,
                        "warnings": result.warnings,
                        "suggestions": result.suggestions,
                        "validation_time": result.validation_time
                    }

                    validation_results["details"].append(file_result)

                    if result.is_valid:
                        validation_results["summary"]["valid_files"] += 1
                    else:
                        validation_results["summary"]["invalid_files"] += 1

                    validation_results["summary"]["total_errors"] += len(result.errors)
                    validation_results["summary"]["total_warnings"] += len(result.warnings)

                except Exception as e:
                    file_result = {
                        "file": str(md_file.relative_to(content_path)),
                        "valid": False,
                        "errors": [f"Error reading file: {str(e)}"],
                        "warnings": [],
                        "suggestions": [],
                        "validation_time": 0
                    }
                    validation_results["details"].append(file_result)
                    validation_results["summary"]["invalid_files"] += 1
                    validation_results["valid"] = False

        # Update overall validity based on results
        if validation_results["summary"]["invalid_files"] > 0:
            validation_results["valid"] = False

        return validation_results

    async def generate_validation_report(
        self,
        validation_results: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Generate a validation report in JSON format

        Args:
            validation_results: Results from content validation
            output_path: Path to save the report

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, indent=2, ensure_ascii=False)

            logger.info(f"Validation report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating validation report: {e}")
            return False


# Example usage
async def main():
    """
    Example of how to use the ContentValidator
    """
    validator = ContentValidator()

    # Example module data
    module_data = {
        "name": "Introduction to AI",
        "description": "An introduction to artificial intelligence concepts",
        "learning_objectives": [
            "Understand basic AI concepts",
            "Learn about different AI approaches"
        ],
        "key_concepts": [
            "Machine Learning",
            "Neural Networks"
        ],
        "chapters": [
            {
                "title": "Chapter 1: What is AI?",
                "description": "Introduction to AI concepts",
                "sections": [
                    {
                        "title": "Introduction",
                        "content": "Artificial Intelligence (AI) is intelligence demonstrated by machines."
                    },
                    {
                        "title": "History of AI",
                        "content": "The history of AI dates back to the 1950s."
                    }
                ],
                "exercises": [
                    {
                        "type": "concept_check",
                        "question": "What is artificial intelligence?",
                        "answer": "Artificial Intelligence is intelligence demonstrated by machines."
                    }
                ]
            }
        ]
    }

    # Validate the module
    result = await validator.validate_module_content(module_data)

    print(f"Module validation result: {'PASS' if result.is_valid else 'FAIL'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    asyncio.run(main())