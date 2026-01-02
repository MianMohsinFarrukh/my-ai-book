---
id: 2
title: plan-rag-chatbot
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: rag-chatbot
branch: 001-rag-chatbot
user: Claude Code
command: /sp.plan
labels: ["planning", "architecture", "rag-chatbot", "docusaurus"]
links:
  spec: F:/my-ai-book/specs/001-rag-chatbot/spec.md
  plan: F:/my-ai-book/specs/001-rag-chatbot/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - F:/my-ai-book/specs/001-rag-chatbot/plan.md
 - F:/my-ai-book/specs/001-rag-chatbot/research.md
 - F:/my-ai-book/specs/001-rag-chatbot/data-model.md
 - F:/my-ai-book/specs/001-rag-chatbot/contracts/openapi.yaml
 - F:/my-ai-book/specs/001-rag-chatbot/quickstart.md
 - F:/my-ai-book/specs/001-rag-chatbot/contracts/
 - F:/my-ai-book/specs/001-rag-chatbot/checklists/requirements.md
tests:
 -
---
## Prompt

```
Architecture Overview:
- Monorepo structure:
  - frontend/ → Docusaurus site
  - backend/ → FastAPI RAG service

Backend Design:
- FastAPI application serving REST endpoints.
- UV used for dependency management and execution.
- OpenAI Agent SDK used to orchestrate reasoning and retrieval.
- Agent Skills used for reusable RAG logic.
- Claude Code Subagents used for ingestion, retrieval, and validation.
- MCP context7 server used as shared context provider.

Core Pipelines:
1. Ingestion Pipeline:
   - Read markdown files from frontend/docs
   - Chunk content
   - Generate embeddings
   - Store vectors in Qdrant

2. Query Pipeline:
   - Accept user question
   - Retrieve relevant chunks from Qdrant
   - Pass context to OpenAI Agent
   - Return grounded response

3. Selected-Text Pipeline:
   - Accept user-selected text
   - Bypass vector search
   - Answer strictly from provided selection

Data Storage:
- Qdrant: vector embeddings
- Neon Postgres: chat history, feedback, logs

Frontend Integration:
- Embedded chatbot page in Docusaurus
- Text selection listener with "Ask AI" action
- Streaming responses

Reusable Intelligence:
- Agent Skills:
  - retrieve_context
  - answer_from_context
  - validate_grounding
- Subagents:
  - ingestion_subagent
  - retrieval_subagent
  - response_guard_subagent

Deployment Plan:
- Backend deployed to cloud (Render/Fly/Railway)
- Frontend deployed via GitHub Vercel
```

## Response snapshot

Completed comprehensive planning for the Integrated RAG Chatbot for Docusaurus Book feature. The planning included:

- Updated plan.md with feature details, technical context, and project structure
- Created research.md with technology evaluations and architecture decisions
- Created data-model.md with database schemas and API contract models
- Created API contracts in OpenAPI format
- Created quickstart.md with setup and usage instructions
- Updated agent context with new technologies

The architecture follows a monorepo structure with separate backend (FastAPI) and frontend (Docusaurus) components. The system implements three core pipelines: ingestion, query, and selected-text processing. Data is stored in Qdrant for vector embeddings and Neon Postgres for chat history.

## Outcome

- ✅ Impact: Created complete architecture plan with data models, API contracts, and implementation guide
- 🧪 Tests: All planning artifacts validated and linked to specification
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/, quickstart.md
- 🔁 Next prompts: Ready for /sp.tasks to generate implementation tasks
- 🧠 Reflection: Planning phase successfully completed with all required artifacts

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All planning artifacts created successfully
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation phase with /sp.tasks