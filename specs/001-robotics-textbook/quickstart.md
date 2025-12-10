# Quickstart Guide: Robotics Textbook Development

## Prerequisites

- Node.js 18+ installed
- Git installed
- ROS 2 Humble Hawksbill installed (for testing code examples)
- Docusaurus CLI: `npm install -g @docusaurus/cli`

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd my-ai-book
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```
   This will start the Docusaurus development server at http://localhost:3000

## Project Structure

```
my-ai-book/
├── docs/                   # Textbook content
│   ├── course-outline/     # Course description
│   ├── module-1/          # Module 1 content
│   ├── module-2/          # Module 2 content
│   ├── module-3/          # Module 3 content
│   ├── module-4/          # Module 4 content
│   └── capstone-project/  # Capstone project
├── src/                   # Custom Docusaurus components
├── static/                # Static assets
├── assets/                # Images, code examples, simulations
└── docusaurus.config.js   # Docusaurus configuration
```

## Adding Content

### Create a New Chapter

1. Create a new directory in the appropriate module:
   ```bash
   mkdir docs/module-1/chapter-4
   ```

2. Add the chapter content:
   ```bash
   # Create the main chapter file
   touch docs/module-1/chapter-4/index.md
   ```

3. Add chapter content with frontmatter:
   ```markdown
   ---
   title: Chapter Title
   sidebar_position: 4
   description: Brief description of the chapter
   ---

   # Chapter Title

   Content goes here...
   ```

### Add Images

1. Place images in the `assets/images/` directory
2. Reference them in your content:
   ```markdown
   ![Alt text](/assets/images/your-image.png)
   ```

### Add Code Examples

1. Place code files in `assets/code-examples/`
2. Reference them in your content:
   ```markdown
   import CodeBlock from '@site/assets/code-examples/example.py';
   ```

## Building and Deployment

### Build Static Site
```bash
npm run build
```
This creates a static site in the `build/` directory.

### Deploy to GitHub Pages
```bash
GIT_USER=<Your GitHub username> npm run deploy
```

## Content Generation Pipeline

The textbook uses Claude Code Router with Spec-Kit Plus skills for automated content generation:

1. **Specify**: Define requirements in the spec
2. **Generate**: Use Claude Code Router to generate content
3. **Refine**: Review and refine generated content
4. **Commit**: Commit the refined content

### Available Skills

- `ros_explainer`: Generate ROS 2 explanations and code
- `robotics_researcher`: Research robotics concepts and best practices
- `isaac_engineer`: Create Isaac Sim content
- `gazebo_builder`: Generate Gazebo simulation content
- `vla_planner`: Plan Vision-Language-Action implementations

## Testing Code Examples

1. Ensure ROS 2 Humble is sourced:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Test Python examples:
   ```bash
   python3 path/to/example.py
   ```

3. For simulation examples, ensure Gazebo is installed and run:
   ```bash
   ros2 launch package_name launch_file.py
   ```

## PDF Generation

The site supports PDF generation through the print functionality or external tools. For best results:

1. Use the browser's print to PDF feature
2. Apply print-specific styles if needed
3. Consider using a dedicated PDF generation tool for bulk conversion

## GitHub Actions Deployment

The repository includes a GitHub Actions workflow for automatic deployment:

1. Push changes to the main branch
2. GitHub Actions will automatically build and deploy the site
3. Check the Actions tab for deployment status