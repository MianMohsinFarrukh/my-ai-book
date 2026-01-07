# PDF Generation for Physical AI & Robotics Textbook

This document describes how to generate PDF versions of the textbook content for offline reading and distribution.

## PDF Generation Tools

The textbook supports multiple PDF generation approaches:

### 1. Docusaurus Plugin Approach
Using `docusaurus-plugin-tailwindcss` and `@docusaurus/plugin-content-docs` with custom CSS for print:

```bash
npm install --save-dev docusaurus-plugin-tailwindcss
```

### 2. Puppeteer-based Generation
Using Puppeteer to convert HTML to PDF:

```bash
npm install puppeteer
```

### 3. Pandoc Conversion
Convert MDX files to PDF via LaTeX:

```bash
# Install pandoc
sudo apt install pandoc texlive-latex-recommended texlive-xetex

# Convert specific document
pandoc -f markdown -t latex --pdf-engine=xelatex -o output.pdf input.mdx
```

## Configuration

### Print CSS Styles

Custom styles for print output:

```css
@media print {
  /* Hide navigation elements */
  .navbar,
  .theme-edit-this-page,
  .pagination-nav,
  .footer {
    display: none !important;
  }

  /* Page breaks */
  .main-wrapper {
    page-break-before: always;
  }

  /* Typography for print */
  body {
    font-family: 'Georgia', serif;
    font-size: 12pt;
    line-height: 1.5;
  }
}
```

### PDF Generation Script

Sample script for generating PDFs:

```javascript
// scripts/generate-pdf.js
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function generatePDF() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Set viewport for consistent rendering
  await page.setViewport({ width: 1200, height: 800 });

  // Navigate to the local site
  await page.goto('http://localhost:3000/docs/course-outline', {
    waitUntil: 'networkidle2'
  });

  // Generate PDF
  const pdf = await page.pdf({
    format: 'A4',
    margin: {
      top: '20px',
      right: '20px',
      bottom: '20px',
      left: '20px'
    }
  });

  // Save PDF
  await fs.promises.writeFile('./output/textbook.pdf', pdf);

  await browser.close();
}

generatePDF().catch(console.error);
```

## Module-Specific PDFs

Each module can be exported as a separate PDF:

- Module 1: `physical-ai-foundations.pdf`
- Module 2: `simulation-environments.pdf`
- Module 3: `isaac-ai-navigation.pdf`
- Module 4: `vla-robotics-capstone.pdf`

## Batch Generation

To generate all PDFs at once:

```bash
# Start local server
npm run start &

# Wait for server to start
sleep 5

# Generate all module PDFs
node scripts/generate-pdf.js --module 1
node scripts/generate-pdf.js --module 2
node scripts/generate-pdf.js --module 3
node scripts/generate-pdf.js --module 4

# Generate complete textbook
node scripts/generate-pdf.js --full
```

## Quality Considerations

- Use vector graphics (SVG) instead of raster images for better print quality
- Ensure sufficient contrast for printed output
- Test rendering across different devices and browsers
- Optimize file sizes for reasonable download times
- Include proper metadata (title, author, subject) in PDFs