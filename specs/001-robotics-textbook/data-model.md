# Data Model: Robotics Textbook

## Entities

### Textbook Module
- **name**: String (e.g., "Physical AI Foundations", "ROS 2 Full Stack", "Simulation Environments", "Humanoid Control")
- **description**: String - Brief overview of the module content
- **chapters**: Array of Chapter entities (exactly 3 chapters per module)
- **learning_objectives**: Array of String - Key concepts students will learn
- **prerequisites**: Array of String - Required knowledge before starting
- **duration**: Number - Estimated time to complete (in hours)

### Chapter
- **title**: String - Chapter name
- **module_id**: String - Reference to parent module
- **content**: String - Chapter content in MDX format
- **figures**: Array of Figure entities - Visual content for the chapter
- **code_examples**: Array of CodeExample entities - Practical implementations
- **exercises**: Array of String - Practice problems for students
- **learning_outcomes**: Array of String - What students should be able to do after completion

### Figure
- **id**: String - Unique identifier
- **title**: String - Description of the figure
- **description**: String - Explanation of what the figure illustrates
- **file_path**: String - Path to the image file in assets/images/
- **type**: String - Category (e.g., "robot_diagram", "sensor_diagram", "pipeline", "ros_graph")
- **alt_text**: String - Accessibility text for screen readers

### Code Example
- **id**: String - Unique identifier
- **title**: String - Brief description of the example
- **language**: String - Programming language (e.g., "python", "urdf", "sdf")
- **code**: String - The actual code content
- **description**: String - Explanation of what the code does
- **file_path**: String - Path to the source file in assets/code-examples/
- **dependencies**: Array of String - ROS packages or libraries required
- **execution_notes**: String - How to run the example

### Simulation Environment
- **id**: String - Unique identifier
- **name**: String - Name of the simulation (e.g., "Gazebo", "Unity")
- **description**: String - Overview of the simulation environment
- **configuration_files**: Array of String - Paths to config files in assets/simulation/
- **setup_instructions**: String - Step-by-step setup guide
- **use_cases**: Array of String - Scenarios where this simulation is applicable

### Capstone Project
- **title**: String - Name of the project
- **description**: String - Overview of the capstone project
- **requirements**: Array of String - What students need to complete the project
- **steps**: Array of String - Sequential steps to complete the project
- **integration_points**: Array of String - How the project connects to modules/chapters
- **evaluation_criteria**: Array of String - How the project will be assessed

### Deployment Guide
- **id**: String - Unique identifier
- **target_platform**: String - Hardware platform (e.g., "Unitree", "Jetson")
- **prerequisites**: Array of String - Requirements before deployment
- **setup_steps**: Array of String - Sequential steps for setup
- **troubleshooting**: Array of String - Common issues and solutions
- **verification_steps**: Array of String - How to verify successful deployment

## Relationships

- Module 1-* Chapter: Each module contains exactly 3 chapters
- Chapter 1-* Figure: Each chapter can contain multiple figures
- Chapter 1-* CodeExample: Each chapter can contain multiple code examples
- Module 1-* SimulationEnvironment: Each module may reference simulation environments
- Module 1-* DeploymentGuide: Each module may reference deployment guides
- CapstoneProject 1-1 Course: The capstone project integrates concepts from all modules

## Validation Rules

- Module.name must be unique within the textbook
- Each module must have exactly 3 chapters
- Each chapter must have at least 1 figure (to meet 50+ figures requirement)
- Each chapter must have at least 1 code example (to meet 20+ examples requirement)
- Figure.file_path must exist in the assets/images directory
- CodeExample.file_path must exist in the assets/code-examples directory
- CodeExample.language must be a supported language (python, urdf, sdf, xml, etc.)
- CapstoneProject.integration_points must reference existing modules/chapters