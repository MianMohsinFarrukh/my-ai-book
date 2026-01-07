# Quickstart Guide: Docusaurus Textbook Enhancement

## Overview
This guide provides step-by-step instructions to implement the three-layer enhancement to the Docusaurus textbook website: Visual Identity, Home Page Redesign, and Blog System.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git for version control
- Access to design tools for logo creation (Figma, Adobe Illustrator, etc.)

## Phase 1: Visual Identity Implementation

### Step 1: Create Logo Assets
1. Design a humanoid-AI inspired logo following the requirements
2. Export in both SVG and PNG formats
3. Create multiple sizes as needed:
   - Navbar: ~100x40 pixels
   - Footer: ~80x32 pixels
4. Place files in `static/img/logo/` directory:
   ```
   static/img/logo/
   ├── logo.svg
   ├── logo.png
   ├── logo-dark.svg (if different dark mode version needed)
   └── logo-dark.png
   ```

### Step 2: Integrate Logo into Docusaurus
1. Update `docusaurus.config.js` to include logo configuration:
   ```javascript
   module.exports = {
     // ... other config
     themeConfig: {
       image: 'img/docusaurus-social-card.jpg', // Update if needed
       navbar: {
         logo: {
           alt: 'Physical AI & Humanoid Robotics Logo',
           src: 'img/logo/logo.svg', // or logo.png
           srcDark: 'img/logo/logo-dark.svg', // if you have a dark mode version
         },
         // ... rest of navbar config
       },
       // ... rest of theme config
     },
   };
   ```

## Phase 2: Home Page Redesign

### Step 1: Create New Home Page Component
1. Replace or update `src/pages/index.js` with new structured layout
2. Implement the six required sections:
   - Hero Section with title and background image
   - Physical AI explanation
   - Embodied Intelligence concepts
   - Technology stack highlights (ROS 2, Gazebo, NVIDIA Isaac, VLA)
   - Learning outcomes
   - Capstone project overview

### Step 2: Add Home Page Images
1. Place high-quality robotics images in `static/img/home/`
2. Ensure images are optimized for web (under 200KB each)
3. Include appropriate alt text for accessibility

### Step 3: Implement Responsive Design
1. Use Docusaurus' built-in CSS classes and Bootstrap components
2. Test across different screen sizes
3. Ensure proper dark/light mode support

## Phase 3: Blog System Implementation

### Step 1: Enable Blog Plugin
1. Update `docusaurus.config.js` to enable blog plugin:
   ```javascript
   module.exports = {
     // ... other config
     presets: [
       [
         'classic',
         /** @type {import('@docusaurus/preset-classic').Options} */
         ({
           // ... other preset options
           blog: {
             path: 'blog',
             routeBasePath: 'blog',
             blogTitle: 'Educational Blog',
             blogDescription: 'Educational content for Physical AI & Humanoid Robotics',
             blogSidebarTitle: 'Recent Posts',
             blogSidebarCount: 'ALL',
             postsPerPage: 'ALL',
             showReadingTime: true,
             feedOptions: {
               type: 'all',
               copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook`,
             },
           },
           // ... other preset options
         }),
       ],
     ],
     // ... rest of config
   };
   ```

### Step 2: Create Initial Blog Posts
1. Create blog posts in the `blog/` directory with proper frontmatter:
   ```markdown
   ---
   title: What is Physical AI?
   date: 2025-01-01
   authors:
     - textbook-team
   description: "Introduction to Physical AI concepts and their importance in robotics"
   tags: [physical-ai, robotics, embodied-intelligence]
   image: /img/blog/physical-ai-concept.jpg
   moduleLink: /docs/modules/module-1/intro
   draft: false
   ---

   Blog content here (800-1200 words)...
   ```

2. Create the initial 5 blog posts:
   - "What is Physical AI?"
   - "Why Humanoid Robots Matter"
   - "ROS 2 as the Robotic Nervous System"
   - "Digital Twins with Gazebo & Isaac"
   - "Vision-Language-Action Robotics"

### Step 3: Add Blog Images
1. Place featured images in `static/img/blog/`
2. Ensure images are optimized for web (under 150KB each)
3. Include appropriate alt text for accessibility

## Phase 4: Quality Validation

### Step 1: Test All Requirements
1. Verify logo appears correctly in navbar and footer across browsers
2. Confirm homepage communicates course value in under 10 seconds
3. Test that all images are optimized
4. Verify blog content is academically accurate
5. Test responsive design on multiple devices
6. Confirm accessibility standards are met

### Step 2: Content Validation
1. Review all content against constitution requirements
2. Verify scientific accuracy of all content
3. Confirm APA citation style is followed where applicable
4. Check that content complexity is appropriate for undergraduate level

## Running the Site
After completing the implementation:

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Serve production build locally for testing
npm run serve
```

## Troubleshooting
- If logo doesn't appear, check file paths and configuration in `docusaurus.config.js`
- If blog posts don't show up, verify correct frontmatter format and file naming
- For responsive issues, check browser developer tools for CSS conflicts
- For accessibility issues, use tools like axe-core or WAVE to identify problems