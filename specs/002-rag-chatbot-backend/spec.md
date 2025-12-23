# Feature Specification: RAG Chatbot Backend

**Feature Branch**: `002-rag-chatbot-backend`
**Created**: 2025-12-19
**Status**: Draft
**Input**: User description: "Integrated RAG Chatbot Development using SpecifyKit Plus, Qwen CLI, Cohere API, FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier Target deployment: Backend API service for an embedded RAG chatbot within a published digital book (e.g., web-based viewer or interactive PDF) Focus: Complete backend implementation of the RAG system, including data ingestion, vector storage, retrieval, generation, and API endpoints – all code and work must be done exclusively inside the pre-existing \"backend\" folder Success criteria: All backend code, configuration files, scripts, tests, and documentation reside strictly within the existing \"backend\" folder (no new top-level folders created) Functional FastAPI server running locally and deployable, with endpoints for querying book content and selected-text mode Successful ingestion of book content chunks into Qdrant using Cohere embeddings RAG pipeline achieves >95% accuracy on test queries and properly isolates context in selected-text mode Response times under 2 seconds for typical queries 80%+ test coverage with passing pytest suite Constraints: Directory structure: All development, code, and files MUST be placed and executed only within the pre-existing \"backend\" folder (e.g., backend/app/, backend/scripts/, backend/tests/, etc.) Technologies & Credentials: Cohere API for embeddings and generation (API key: 91TCPoZqUmyLkhtqZnnzR0mSezzlfRXaMgwy4zu1) Qwen CLI for local prototyping and testing of prompts/generation logic SpecifyKit Plus for defining schemas, workflows, and project specifications FastAPI for the API server Neon Serverless Postgres for structured metadata/storage (DB URL: postgresql://neondb_owner:npg_3KsHFmVEa5lB@ep-hidden-truth-ablhtq3f-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require) Qdrant Cloud Free Tier for vector storage (API key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.w0WuOCsRTJZnQZ1Y3le4ect8QLkyloCP2PPJBYU5o6U, Cluster URL: https://afcd9119-6ed1-4195-87b1-0e1fc94a1ae7.eu-west-2-0.aws.cloud.qdrant.io/, Cluster ID: afcd9119-6ed1-4195-87b1-0e1fc94a1ae7) Resource limits: Stay within Qdrant Free Tier (max 1GB), use Cohere embed-english-v3.0 or similar low-dimension model (<512 dims) Security: All API keys and credentials loaded via environment variables or secure config inside backend folder only (never hard-coded in committed files) Development: Python code follows PEP 8, fully containerized with Docker, deployable to free platforms Timeline: Backend prototype in 1 week, complete backend with tests in 4 weeks Not building: Frontend UI or book viewer integration (only provide API endpoints and embedding instructions) Any code or files outside the existing \"backend\" folder Additional paid services or upgrades beyond free tiers Multi-user authentication or session persistence Advanced monitoring, logging services, or CI/CD pipelines beyond basic setup"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Query Book Content via RAG (Priority: P1)

As a user reading a digital book, I want to ask questions about the book content and receive accurate answers based on the book's information, so that I can better understand the material without having to manually search through the text.

**Why this priority**: This is the core functionality of the RAG chatbot - providing accurate answers from book content, which is the primary value proposition.

**Independent Test**: Can be fully tested by ingesting sample book content, querying the API with questions about the content, and verifying that responses are accurate and relevant to the book material.

**Acceptance Scenarios**:

1. **Given** book content has been ingested into the system, **When** a user submits a question about the book content, **Then** the system returns an accurate answer based on the book content within 2 seconds
2. **Given** book content has been ingested into the system, **When** a user submits a question unrelated to the book content, **Then** the system responds appropriately indicating it cannot answer based on the provided content

---

### User Story 2 - Query with Selected Text Context (Priority: P2)

As a user reading a digital book, I want to select specific text and ask questions about only that selected text, so that I can get contextually relevant answers without interference from other parts of the book.

**Why this priority**: This provides the specialized selected-text mode functionality that differentiates the chatbot and enables focused queries on specific passages.

**Independent Test**: Can be tested by providing selected text along with a question and verifying that the response is based solely on the provided text, without referencing other book content.

**Acceptance Scenarios**:

1. **Given** a user has selected specific text from the book, **When** the user submits a question with the selected text context, **Then** the system returns an answer based only on the provided selected text within 2 seconds
2. **Given** a user has selected specific text from the book, **When** the user submits a question that cannot be answered from the selected text, **Then** the system responds appropriately indicating insufficient context

---

### User Story 3 - Ingest and Store Book Content (Priority: P2)

As a content manager, I want to upload book content that gets properly chunked, embedded, and stored in the vector database, so that users can later query the content effectively.

**Why this priority**: This is the foundational data pipeline that enables the query functionality, but can be tested independently with a simple API.

**Independent Test**: Can be tested by uploading book content and verifying it's properly stored in the vector database with correct embeddings.

**Acceptance Scenarios**:

1. **Given** book content is provided for ingestion, **When** the ingestion process runs, **Then** the content is properly chunked, embedded using Cohere API, and stored in Qdrant vector database
2. **Given** book content has been ingested, **When** system checks the stored embeddings, **Then** they are retrievable and properly indexed for semantic search

---

### Edge Cases

- What happens when a query is submitted but no book content has been ingested yet?
- How does the system handle extremely long book content that approaches Qdrant Free Tier limits?
- What happens when a user submits a malformed query or query with no semantic meaning?
- How does the system handle API rate limits from Cohere or Qdrant services?
- What happens when the vector database is temporarily unavailable?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide an API endpoint for querying book content using RAG methodology
- **FR-002**: System MUST accept user questions and return accurate answers based on ingested book content
- **FR-003**: System MUST provide a separate endpoint for querying with selected text context
- **FR-004**: System MUST generate semantic embeddings for book content chunks
- **FR-005**: System MUST store and retrieve vector embeddings for semantic search
- **FR-006**: System MUST store metadata in a structured database
- **FR-007**: System MUST respond to queries within 2 seconds for typical requests
- **FR-008**: System MUST process and ingest book content into vector storage
- **FR-009**: System MUST ensure query responses are grounded in the provided book content to minimize hallucinations
- **FR-010**: System MUST implement proper error handling and return appropriate status codes
- **FR-011**: System MUST operate within specified resource limits for storage and computation
- **FR-012**: System MUST load API keys and credentials securely
- **FR-013**: System MUST be deployable using containerization
- **FR-014**: System MUST include comprehensive test coverage (80%+)

*Example of marking unclear requirements:*

- **FR-015**: System MUST handle multiple book content formats (PDF, plain text, markdown, HTML)

### Key Entities *(include if feature involves data)*

- **Book Content**: Represents the digital book material that has been ingested, including metadata like title, author, and content chunks
- **Vector Embeddings**: Represents the vector representations of book content chunks stored in Qdrant for semantic search
- **Query Request**: Represents a user's question along with optional selected text context
- **Response**: Represents the AI-generated answer based on book content with confidence indicators

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Users can query book content and receive accurate answers within 2 seconds response time
- **SC-002**: RAG pipeline achieves >95% accuracy on test queries compared to expected answers from book content
- **SC-003**: System properly isolates context when using selected-text mode, avoiding leakage from other book content
- **SC-004**: All system code, configuration files, scripts, tests, and documentation reside strictly within the designated backend folder structure
- **SC-005**: Test suite achieves 80%+ code coverage with all tests passing
- **SC-006**: System operates within specified resource limits for storage and computational requirements
- **SC-007**: System is successfully containerized and deployable to standard platforms