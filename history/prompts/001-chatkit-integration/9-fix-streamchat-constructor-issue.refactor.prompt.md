---
id: 9
title: Fix StreamChat Constructor Issue
stage: refactor
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-chatkit-integration
branch: 001-chatkit-integration
user: user
command: manual
labels: [bugfix, streamchat, constructor]
links:
  spec: ../specs/001-chatkit-integration/spec.md
  tasks: ../specs/001-chatkit-integration/tasks.md
  ticket: null
  adr: null
  pr: null
files:
 - frontend/src/components/Chatbot/Chatbot.jsx
tests:
---

## Prompt

Fix the "window.StreamChat.getInstance is not a constructor" runtime error in the existing StreamChat component that was interfering with the ChatKit implementation.

## Response snapshot

Fixed the "window.StreamChat.getInstance is not a constructor" runtime error in frontend/src/components/Chatbot/Chatbot.jsx by correcting the StreamChat initialization. The original code used `new window.StreamChat.getInstance(STREAM_API_KEY)` which is incorrect API usage. The fix changes to `new window.StreamChat(STREAM_API_KEY)` and updates the dynamic import to assign `StreamChat` directly instead of creating a wrapper object. This resolves the constructor error while maintaining the existing StreamChat functionality that may be used alongside the new ChatKit implementation.

## Outcome

- ✅ Impact: Resolved runtime error that was preventing proper page loading
- 🧪 Tests: StreamChat component now initializes without constructor errors
- 📁 Files: 1 file updated to fix the StreamChat API usage
- 🔁 Next prompts: Both StreamChat and ChatKit implementations can coexist
- 🧠 Reflection: Correct API usage prevents constructor-related runtime errors

## Evaluation notes (flywheel)

- Failure modes observed: TypeError during StreamChat initialization
- Graders run and results (PASS/FAIL): StreamChat initialization now passes
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify both implementations can run together