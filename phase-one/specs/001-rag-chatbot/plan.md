# Implementation Plan: Integrated RAG Chatbot for Docusaurus Book

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-17 | **Spec**: [specs/001-rag-chatbot/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a Retrieval-Augmented Generation (RAG) chatbot for a Docusaurus-based book that answers user questions based on book content, with special handling for user-selected text context. The solution uses a FastAPI backend with OpenAI Agents and Claude for RAG processing, Neon Serverless Postgres for storage, and Qdrant Cloud for vector embeddings. The frontend integrates as a client-only React module in Docusaurus to avoid SSR issues.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript/TypeScript (Node.js 18+) + React 18+ (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agent SDK, Qdrant, Neon Postgres, Docusaurus 3.x, React 18+
**Storage**: Neon Serverless Postgres (relational data), Qdrant Cloud (vector embeddings), Docusaurus markdown files (content source)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web browser (Chrome, Firefox, Safari, Edge) for frontend, Linux server for backend
**Project Type**: Web application (frontend + backend architecture)
**Performance Goals**: <5 seconds for query response, 95% accuracy for content-based answers, 90% relevance for selected-text queries
**Constraints**: No hallucination beyond provided context, selected-text queries override global retrieval, only book content as knowledge source, Docusaurus SSR compatibility (client-only execution)
**Scale/Scope**: Local/internal testing deployment, single book project, 100 concurrent users capacity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the project constitution for the Physical AI & Humanoid Robotics textbook, this implementation plan is compliant:
- The RAG chatbot feature enhances the educational experience by providing immediate access to book content information
- Implementation follows reproducible standards with documented code and reusable agent skills
- The solution maintains the progressive learning approach by providing contextual help without disrupting the reading experience
- Scientific accuracy is maintained by enforcing strict adherence to book content without hallucination
- The implementation supports the hands-on focus by providing accurate answers about ROS 2, Gazebo, and Isaac Sim concepts
- No violations of the core principles, standards, or constraints identified

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── book_content.py      # Book content entities
│   │   ├── chat_session.py      # Chat session entities
│   │   └── vector_embeddings.py # Vector embedding entities
│   ├── services/
│   │   ├── rag_service.py       # RAG query processing
│   │   ├── embedding_service.py # Embedding generation and management
│   │   ├── chat_service.py      # Chat session management
│   │   └── ingestion_service.py # Content ingestion pipeline
│   └── api/
│       ├── main.py              # FastAPI application
│       ├── routes/
│       │   ├── chat.py          # Chat endpoints
│       │   ├── query.py         # Query endpoints
│       │   └── ingest.py        # Ingestion endpoints
│       └── dependencies.py      # API dependencies
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   └── RAGChatbot/          # Client-only RAG chatbot module
│   │       ├── RAGChatbot.jsx   # Main chatbot component
│   │       ├── ChatWindow.jsx   # Chat interface window
│   │       └── TextSelector.jsx # Text selection handler
│   ├── clientModules/
│   │   └── rag-chatbot.js       # Docusaurus client module injection
│   ├── pages/
│   └── services/
│       └── api.js               # API service for chat communication
└── docs/
    └── module-3/
        └── chapter-1/
            └── index.md         # Documentation for the RAG chatbot feature
```

**Structure Decision**: Web application structure selected with separate backend and frontend directories to maintain separation of concerns. The RAG chatbot component will be integrated into the Docusaurus documentation site using clientModules approach to ensure browser-only execution and prevent SSR issues.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
