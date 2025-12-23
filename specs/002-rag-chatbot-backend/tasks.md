---
description: "Task list for RAG Chatbot Backend implementation"
---

# Tasks: RAG Chatbot Backend

**Input**: Design documents from `/specs/002-rag-chatbot-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per constitution (80%+ coverage) and spec requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` at repository root
- **Source**: `backend/app/`
- **Scripts**: `backend/scripts/`
- **Tests**: `backend/tests/`
- **Config**: `backend/requirements.txt`, `backend/.env`, `backend/Dockerfile`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per implementation plan
- [x] T002 Create requirements.txt with Python dependencies in backend/requirements.txt
- [x] T003 [P] Create .env file for credentials in backend/.env
- [x] T004 [P] Create Dockerfile in backend/Dockerfile
- [x] T005 Create initial project structure in backend/app/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Setup configuration management with python-dotenv in backend/app/config.py
- [x] T007 [P] Implement Cohere API client wrapper in backend/app/services/cohere_client.py
- [x] T008 [P] Setup Qdrant client and connection in backend/app/services/qdrant_client.py
- [x] T009 Setup database connection for Neon Postgres in backend/app/services/postgres_client.py
- [x] T010 Create Pydantic models for data validation in backend/app/models/request.py
- [x] T011 Create Pydantic models for data validation in backend/app/models/response_model.py
- [x] T012 Setup FastAPI app structure in backend/app/main.py
- [x] T013 Setup error handling and logging infrastructure in backend/app/utils/error_handler.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 3 - Ingest and Store Book Content (Priority: P2) 🎯 Prerequisite for other stories

**Goal**: Enable content managers to upload book content that gets properly chunked, embedded, and stored in vector database for later querying

**Independent Test**: Can be tested by uploading book content and verifying it's properly stored in the vector database with correct embeddings

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US3] Contract test for ingestion endpoint in backend/tests/contract/test_ingestion.py
- [x] T015 [P] [US3] Integration test for book ingestion in backend/tests/integration/test_book_ingestion.py

### Implementation for User Story 3

- [x] T016 [P] [US3] Create BookContent model in backend/app/models/book_content.py
- [x] T017 [P] [US3] Create ContentChunk model in backend/app/models/content_chunk.py
- [x] T018 [US3] Implement text chunking utility in backend/app/utils/chunking.py
- [x] T019 [US3] Implement book ingestion service in backend/app/services/ingestion_service.py
- [x] T020 [US3] Create ingestion script in backend/scripts/ingest_book.py
- [x] T021 [US3] Add ingestion endpoint in backend/app/routers/ingestion.py
- [x] T022 [US3] Add validation and error handling for ingestion

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 4: User Story 1 - Query Book Content via RAG (Priority: P1)

**Goal**: Enable users to ask questions about book content and receive accurate answers based on the book's information

**Independent Test**: Can be fully tested by ingesting sample book content, querying the API with questions about the content, and verifying that responses are accurate and relevant to the book material

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US1] Contract test for query endpoint in backend/tests/contract/test_query.py
- [x] T024 [P] [US1] Integration test for book content query in backend/tests/integration/test_book_query.py

### Implementation for User Story 1

- [x] T025 [P] [US1] Create QueryRequest model in backend/app/models/query_request.py
- [x] T026 [P] [US1] Create Response model in backend/app/models/response_model.py
- [x] T027 [US1] Implement retrieval service in backend/app/services/retrieval_service.py
- [x] T028 [US1] Implement generation service in backend/app/services/generation_service.py
- [x] T029 [US1] Implement main query service in backend/app/services/query_service.py
- [x] T030 [US1] Add query endpoint in backend/app/routers/query.py
- [x] T031 [US1] Add validation and error handling for query functionality

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 5: User Story 2 - Query with Selected Text Context (Priority: P2)

**Goal**: Enable users to select specific text and ask questions about only that selected text, getting contextually relevant answers without interference from other parts of the book

**Independent Test**: Can be tested by providing selected text along with a question and verifying that the response is based solely on the provided text, without referencing other book content

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T032 [P] [US2] Contract test for selected text query endpoint in backend/tests/contract/test_selected_text.py
- [x] T033 [P] [US2] Integration test for selected text query in backend/tests/integration/test_selected_text_query.py

### Implementation for User Story 2

- [x] T034 [P] [US2] Update QueryRequest model to support selected text mode in backend/app/models/query_request.py
- [x] T035 [US2] Implement selected text mode in retrieval service in backend/app/services/retrieval_service.py
- [x] T036 [US2] Implement selected text context isolation in generation service in backend/app/services/generation_service.py
- [x] T037 [US2] Add selected text query functionality to main query service in backend/app/services/query_service.py
- [x] T038 [US2] Update query endpoint to support selected text mode in backend/app/routers/query.py
- [x] T039 [US2] Add validation and error handling for selected text functionality

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 6: API Endpoints Integration and Health Checks

**Goal**: Complete API with health check and proper endpoint registration

- [x] T040 Create health check endpoint in backend/app/routers/health.py
- [x] T041 Register all routers in backend/app/main.py
- [x] T042 Add API key authentication middleware in backend/app/middleware/auth.py
- [x] T043 Setup API documentation (Swagger) in backend/app/main.py

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T044 [P] Update README.md in backend/ with setup instructions
- [x] T045 Code cleanup and refactoring across all modules
- [x] T046 Performance optimization to meet <2s response time in backend/app/services/*
- [x] T047 [P] Additional unit tests to achieve 80%+ coverage in backend/tests/unit/
- [x] T048 Security hardening (API key validation, input sanitization)
- [x] T049 Run quickstart.md validation with actual implementation

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

- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories but is required for US1 and US2
- **User Story 1 (P1)**: Depends on User Story 3 (content must be ingested first) - Can be independently testable after content is available
- **User Story 2 (P2)**: Depends on User Story 3 (content must be ingested first) - Can be independently testable after content is available

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for query endpoint in backend/tests/contract/test_query.py"
Task: "Integration test for book content query in backend/tests/integration/test_book_query.py"

# Launch all models for User Story 1 together:
Task: "Create QueryRequest model in backend/app/models/query_request.py"
Task: "Create Response model in backend/app/models/response_model.py"
```

---

## Implementation Strategy

### MVP First (User Stories 3 and 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 3 (ingestion - required for other stories)
4. Complete Phase 4: User Story 1 (core query functionality)
5. **STOP and VALIDATE**: Test User Stories 3 and 1 together independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 3 → Test independently → Provides content for other stories
3. Add User Story 1 → Test independently → Core functionality MVP!
4. Add User Story 2 → Test independently → Enhanced functionality
5. Add Phase 6-7 → Production ready API with health checks and polish
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 3 (ingestion)
   - Developer B: User Story 1 (query) - can start after ingestion is complete
   - Developer C: User Story 2 (selected text) - can start after ingestion is complete
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