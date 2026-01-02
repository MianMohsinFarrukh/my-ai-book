# Testing the ChatKit Implementation

## Manual Testing Steps

1. **Start the Docusaurus development server:**
   ```bash
   cd frontend
   npm run start
   ```

2. **Verify the floating toggle button appears:**
   - Open the documentation site in a browser
   - Check that the floating chat button appears in the bottom-right corner
   - Verify it has the chat emoji (💬) and proper styling

3. **Test the text selection functionality:**
   - Select text on any documentation page
   - Open the chat interface
   - Verify that the selected text appears as context in the chat input area

4. **Test the chat functionality:**
   - Click the floating toggle to open the chat interface
   - Verify the chat window appears with proper styling
   - Send a message and verify it appears in the chat history
   - Check that the AI response is received and displayed
   - Verify the loading state shows "Thinking..." while waiting for response

5. **Test the close functionality:**
   - Click the close button (×) in the chat header
   - Verify the chat interface closes and the floating toggle reappears

6. **Test responsiveness:**
   - Resize the browser window to test mobile responsiveness
   - Verify the chat interface and toggle button adapt to different screen sizes

7. **Test across different pages:**
   - Navigate to different documentation pages
   - Verify the chatbot remains available and functional on all pages
   - Check that text selection context works on all pages

8. **Test error handling:**
   - Try sending empty messages (should be disabled)
   - Test with network errors (should show error message)

## Expected Behavior

- The chatbot should be available on all documentation pages
- The interface should be responsive and work on mobile and desktop
- Text selection context should be captured and displayed
- Messages should be exchanged with the backend AI service
- No console errors should appear
- No layout override crashes should occur
- The SSR should work properly without crashes