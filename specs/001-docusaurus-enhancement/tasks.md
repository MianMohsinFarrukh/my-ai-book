---
description: "Task list for Docusaurus Textbook Enhancement implementation"
---

# Tasks: Docusaurus Textbook Enhancement

**Input**: Design documents from `/specs/001-docusaurus-enhancement/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Docusaurus project**: `docs/`, `src/`, `static/`, `blog/` at repository root
- **Configuration**: `docusaurus.config.js`, `package.json` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create required directory structure for assets in static/img/
- [x] T002 [P] Create static/img/logo/ directory for logo assets
- [x] T003 [P] Create static/img/home/ directory for homepage images
- [x] T004 [P] Create static/img/blog/ directory for blog images

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create logo design specifications based on research requirements
- [x] T006 Update docusaurus.config.js to prepare for logo integration
- [x] T007 Enable blog plugin in docusaurus.config.js
- [x] T008 [P] Prepare homepage structure by creating index.mdx if it doesn't exist
- [x] T009 [P] Create blog directory if it doesn't exist

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access Enhanced Educational Content (Priority: P1) 🎯 MVP

**Goal**: Redesign the home page with structured sections explaining Physical AI, technology stack highlights, and learning outcomes

**Independent Test**: Can be fully tested by visiting the home page and navigating through the content, delivering a professional learning experience with clear explanations and visual aids.

### Implementation for User Story 1

- [x] T010 [P] [US1] Create hero section component for homepage in src/components/HeroSection.jsx
- [x] T011 [P] [US1] Create Physical AI explanation section in src/components/PhysicalAISection.jsx
- [x] T012 [P] [US1] Create Embodied Intelligence section in src/components/EmbodiedIntelligenceSection.jsx
- [x] T013 [P] [US1] Create Technology Stack section in src/components/TechnologyStackSection.jsx
- [x] T014 [P] [US1] Create Learning Outcomes section in src/components/LearningOutcomesSection.jsx
- [x] T015 [P] [US1] Create Capstone Project section in src/components/CapstoneProjectSection.jsx
- [x] T016 [US1] Create homepage index.mdx using the new components
- [x] T017 [US1] Add humanoid robot images to static/img/home/ directory
- [x] T018 [US1] Implement responsive layout for all homepage sections
- [x] T019 [US1] Add proper heading hierarchy (h1 for main title, h2 for sections) to homepage
- [x] T020 [US1] Add accessibility attributes (alt text) to all homepage images

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Access Professional Visual Identity (Priority: P1)

**Goal**: Display a professional logo that represents Physical AI & Embodied Intelligence concepts in navbar and footer

**Independent Test**: Can be fully tested by viewing the website and confirming the logo appears in the navbar and footer, delivering a professional brand identity that represents the core concepts.

### Implementation for User Story 2

- [x] T021 [US2] Generate professional Physical AI logo with humanoid + AI brain concepts
- [x] T022 [US2] Export logo as SVG format in static/img/logo/logo.svg
- [x] T023 [US2] Export logo as PNG format in static/img/logo/logo.png
- [x] T024 [US2] Create dark mode version of logo as static/img/logo/logo-dark.svg (if needed)
- [x] T025 [US2] Update docusaurus.config.js navbar logo configuration
- [x] T026 [US2] Verify logo appears correctly in navbar across different browsers
- [x] T027 [US2] Verify logo scales appropriately on different devices
- [x] T028 [US2] Test logo visibility in both dark and light modes

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Access Complementary Educational Blog (Priority: P2)

**Goal**: Provide an educational blog system that complements the textbook content with image-rich, research-aligned posts mapped to course modules

**Independent Test**: Can be fully tested by browsing the blog section and reading posts, delivering research-aligned content that enhances the learning experience.

### Implementation for User Story 3

- [x] T029 [US3] Create first educational blog post: "Physical AI Explained" in blog/2025-01-01-physical-ai-explained.md
- [x] T030 [US3] Create second educational blog post: "Humanoid Robotics Importance" in blog/2025-01-08-humanoid-robotics-importance.md
- [x] T031 [US3] Create third educational blog post: "ROS 2 Architecture" in blog/2025-01-15-ros2-architecture.md
- [x] T032 [US3] Create fourth educational blog post: "Sim-to-Real using Gazebo & Isaac" in blog/2025-01-22-sim-to-real.md
- [x] T033 [US3] Create fifth educational blog post: "Vision-Language-Action Systems" in blog/2025-01-29-vla-systems.md
- [x] T034 [P] [US3] Add relevant robotics images to each blog post in static/img/blog/
- [x] T035 [US3] Link blog posts to corresponding course modules using moduleLink frontmatter
- [x] T036 [US3] Ensure each blog post has 800-1200 words of educational content
- [x] T037 [US3] Add proper APA-style citations to blog posts where applicable
- [x] T038 [US3] Validate blog post frontmatter follows required schema (title, date, authors, description, tags)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T039 [P] Update navigation structure to include blog link
- [x] T040 [P] Add accessibility improvements across all pages
- [x] T041 [P] Optimize all images for web delivery (logo < 50KB, home images < 200KB, blog images < 150KB)
- [x] T042 [P] Test responsive layout on different screen sizes
- [x] T043 [P] Validate site builds successfully with `npm run build`
- [x] T044 [P] Test navigation between all pages and blog posts
- [x] T045 [P] Run accessibility audit using tools like axe-core
- [x] T046 [P] Validate all links work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Create hero section component for homepage in src/components/HeroSection.jsx"
Task: "Create Physical AI explanation section in src/components/PhysicalAISection.jsx"
Task: "Create Embodied Intelligence section in src/components/EmbodiedIntelligenceSection.jsx"
Task: "Create Technology Stack section in src/components/TechnologyStackSection.jsx"
Task: "Create Learning Outcomes section in src/components/LearningOutcomesSection.jsx"
Task: "Create Capstone Project section in src/components/CapstoneProjectSection.jsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Homepage redesign)
   - Developer B: User Story 2 (Logo implementation)
   - Developer C: User Story 3 (Blog system)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence