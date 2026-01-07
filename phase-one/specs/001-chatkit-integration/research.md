# Research: AI Book Assistant ChatKit Implementation

## Decision: Docusaurus clientModules Integration Approach
**Rationale**: Using Docusaurus clientModules is the officially supported approach for injecting client-side functionality into Docusaurus applications. This ensures the chatbot only runs in the browser, preventing SSR crashes and layout override issues. The clientModules approach allows the chatbot to be injected at the app root level and persist across page navigations.

**Alternatives considered**:
- Layout.jsx injection: Would cause SSR issues and layout override crashes as mentioned in requirements
- Theme wrapper: More complex implementation with potential for conflicts
- Direct DOM injection: Less maintainable and not following Docusaurus best practices

## Decision: ChatKit Library for UI
**Rationale**: ChatKit provides a modern, professional chat UI out-of-the-box without requiring custom CSS implementation. It offers responsive design, typing indicators, message bubbles, and avatars with minimal configuration. This aligns with the requirement for a clean, professional UI without custom CSS.

**Alternatives considered**:
- Custom chat UI: Would violate the "no custom CSS" requirement and require significant development time
- Stream Chat React: Would require custom styling to match the professional UI requirement
- Simple React components: Would require more implementation work to achieve professional appearance

## Decision: React Portal for Floating Interface
**Rationale**: Using React portals allows the chatbot to be rendered at the app root level while maintaining its own lifecycle independent of page changes. This ensures the chatbot remains available across all documentation pages and doesn't get destroyed during navigation.

**Alternatives considered**:
- Embedding in Layout: Would cause layout override issues
- Component per page: Would result in multiple instances and inconsistent state
- Global state management: Would still require a root-level mounting point

## Technology Best Practices

### Docusaurus clientModules
- Use the clientModules API to inject the chatbot at the App level
- Ensure the module only executes in browser environments
- Follow Docusaurus' official documentation for client module patterns
- Handle potential conflicts with other client modules

### ChatKit Integration
- Leverage ChatKit's built-in themes and styling
- Customize only through theme variables as specified
- Ensure accessibility compliance with ChatKit components
- Handle responsive design through ChatKit's built-in features

### Browser-Only Execution
- Verify window and document objects exist before executing chatbot code
- Use Docusaurus' BrowserOnly component where appropriate
- Implement proper error handling for SSR environments
- Ensure no server-side rendering of chatbot components

## Implementation Considerations

### Performance
- Lazy load chatbot components to minimize initial bundle impact
- Implement proper cleanup to prevent memory leaks
- Optimize for minimal impact on page load times
- Consider virtualization for long message histories

### Text Selection Context
- Implement document-level event listeners for text selection
- Ensure text selection works across different page navigations
- Pass selected text context to the AI backend service
- Handle edge cases like multi-line selections and large text blocks

### Mobile Responsiveness
- Test ChatKit's responsive features across different device sizes
- Ensure the floating toggle button is accessible on mobile
- Optimize touch targets for mobile interaction
- Consider mobile-specific UI adjustments within ChatKit's capabilities