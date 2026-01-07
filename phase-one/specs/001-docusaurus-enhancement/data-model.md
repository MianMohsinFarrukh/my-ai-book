# Data Model: Docusaurus Textbook Enhancement

## Entities from Feature Specification

### 1. Website Logo
- **Name**: Website Logo
- **Fields**:
  - `id`: string (unique identifier)
  - `name`: string (logo name/description)
  - `formats`: array (SVG, PNG)
  - `dimensions`: object (width, height in pixels)
  - `path`: string (relative path in static/img/logo/)
  - `altText`: string (accessibility description)
  - `usageContexts`: array (navbar, footer)
- **Validation rules**:
  - Must support both dark and light mode display
  - File size must be optimized for web delivery
  - Dimensions appropriate for navbar and footer contexts
- **Relationships**: None

### 2. Home Page Section
- **Name**: Home Page Section
- **Fields**:
  - `id`: string (unique identifier for section)
  - `title`: string (section heading)
  - `content`: string (Markdown/MDX content)
  - `order`: number (display order 1-6)
  - `componentType`: string (hero, explanation, technology, outcome, project)
  - `imageUrl`: string (optional path to associated image)
  - `altText`: string (accessibility description for image)
- **Validation rules**:
  - Must include required sections: Hero, Physical AI, Embodied Intelligence, Technology Stack, Learning Outcomes, Capstone Project
  - Content must align with scientific accuracy standards
  - Responsive design requirements met
- **State transitions**: None
- **Relationships**: Part of Home Page entity

### 3. Educational Blog Post
- **Name**: Educational Blog Post
- **Fields**:
  - `id`: string (unique identifier, typically date-based filename)
  - `title`: string (blog post title)
  - `date`: string (ISO 8601 date format)
  - `authors`: array (author names)
  - `tags`: array (technology tags, module references)
  - `description`: string (meta description)
  - `image`: string (path to featured image)
  - `altText`: string (accessibility description for featured image)
  - `content`: string (Markdown/MDX content, 800-1200 words)
  - `moduleLink`: string (reference to related course module)
  - `wordCount`: number (between 800-1200)
- **Validation rules**:
  - Content must be academically accurate and peer-reviewed
  - Word count between 800-1200 words
  - Must include proper citations in APA style
  - Must link to relevant textbook modules
- **Relationships**: Related to Course Modules

### 4. Course Module
- **Name**: Course Module
- **Fields**:
  - `id`: string (module identifier, e.g., "module-1")
  - `title`: string (module title)
  - `description`: string (module overview)
  - `chapters`: array (chapter titles)
  - `learningObjectives`: array (learning objectives)
  - `relatedBlogPosts`: array (blog post IDs)
- **Validation rules**:
  - Must contain exactly 3 chapters per module
  - Learning objectives must align with textbook content
- **Relationships**: Connected to Blog Posts

### 5. Image Asset
- **Name**: Image Asset
- **Fields**:
  - `id`: string (unique identifier)
  - `name`: string (file name without extension)
  - `path`: string (relative path from static/img/)
  - `category`: string (logo, home, blog)
  - `dimensions`: object (width, height in pixels)
  - `fileSize`: number (in bytes)
  - `altText`: string (accessibility description)
  - `usageContexts`: array (where image is used)
  - `optimized`: boolean (whether image is optimized for web)
- **Validation rules**:
  - File size must be optimized for web delivery
  - Alt text required for accessibility
  - Appropriate dimensions for usage context
- **Relationships**: Used by Logo, Home Page, Blog Post entities