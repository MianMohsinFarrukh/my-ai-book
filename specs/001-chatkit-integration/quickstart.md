# Quickstart Guide: AI Book Assistant (ChatKit-based)

## Prerequisites
- Node.js 18+ installed
- Docusaurus 3.x project set up
- Access to existing AI backend service
- ChatKit library access

## Installation

1. Install required dependencies:
```bash
npm install chatkit-ui  # or whatever ChatKit library is used
```

2. Verify your project has the required dependencies:
```bash
npm list react react-dom @docusaurus/core
```

## Basic Setup

### 1. Create the ChatKit Components
Create a new component at `frontend/src/components/ChatKit/ChatKitBot.jsx`:

```jsx
import React, { useState } from 'react';
// ChatKit library imports
```

### 2. Set up Docusaurus clientModule
Create a client module at `frontend/src/clientModules/chatbot.js`:

```javascript
// Client module to inject chatbot at app root level
```

### 3. Integrate with Existing AI Service
Connect the ChatKit component with your existing AI backend service for processing queries.

### 4. Add Text Selection Handling
Implement document-level event listeners to capture selected text for context.

## Running Locally

1. Start your Docusaurus development server:
```bash
npm run start
```

2. The chatbot should be available on all documentation pages via the floating icon.

## Testing the Integration

1. Open any documentation page
2. Click the floating chat icon to open the interface
3. Verify that:
   - The chat interface opens smoothly without layout disruption
   - The interface works on both mobile and desktop
   - Text selection context is captured properly
   - Messages are sent and received correctly
   - No console errors occur

## Text Selection Feature

The text selection context feature should work automatically. To test:
1. Select text on any documentation page
2. Initiate a chat query
3. Verify that the selected text is included as context for the AI query

## Mobile Responsiveness

Test the chat interface on various screen sizes:
- Mobile (320px - 768px)
- Tablet (768px - 1024px)
- Desktop (1024px+)

Ensure the floating icon and chat window adapt properly to different screen sizes.