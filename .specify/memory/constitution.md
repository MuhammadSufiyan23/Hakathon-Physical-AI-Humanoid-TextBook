<!-- Sync Impact Report -->
<!-- Version change: 1.0.0 -> 1.1.0 -->
<!-- Modified principles: Changed from Physical AI & Humanoid Robotics to RAG Chatbot Development -->
<!-- Added sections: RAG-specific principles, Cohere API usage, Vector database constraints -->
<!-- Removed sections: Previous robotics-specific principles -->
<!-- Templates requiring updates:
✅ .specify/templates/plan-template.md
✅ .specify/templates/spec-template.md
✅ .specify/templates/tasks-template.md
✅ .claude/commands/sp.adr.md
✅ .claude/commands/sp.analyze.md
✅ .claude/commands/sp.checklist.md
✅ .claude/commands/sp.clarify.md
✅ .claude/commands/sp.constitution.md
✅ .claude/commands/sp.git.commit_pr.md
✅ .claude/commands/sp.implement.md
✅ .claude/commands/sp.phr.md
✅ .claude/commands/sp.plan.md
✅ .claude/commands/sp.specify.md
✅ .claude/commands/sp.tasks.md
-->
<!-- Follow-up TODOs: None -->

# Integrated RAG Chatbot Development Constitution

## Core Principles

### I. Accuracy in Retrieval and Generation
All responses MUST be grounded in retrieved book content or selected text to minimize hallucinations, using vector-based search and Cohere-powered augmentation for factual correctness.

### II. Usability for End-Users
The chatbot interface MUST be intuitive with fast response times under 2 seconds, providing a seamless experience for users querying book content.

### III. Modularity
Components like retrieval, database, and API MUST be loosely coupled for easy maintenance, allowing independent updates and testing of individual system parts.

### IV. Security
API keys MUST be encrypted, data privacy MUST be maintained with no user data logging, and all sensitive information MUST be handled securely in compliance with privacy regulations.

### V. Excellence in Implementation
Code MUST follow PEP 8 standards for Python, with optimized performance and multilingual support via Cohere/Qwen, ensuring clean, maintainable implementation.

## Key Standards and Constraints

All responses must be grounded in retrieved book content or selected text to minimize hallucinations.

Code Quality Standards:
- Python code MUST follow PEP 8 standards
- Test coverage MUST be 80%+ using pytest
- Integration testing MUST include end-to-end tests for RAG pipeline using mock data
- Documentation MUST be comprehensive with README and inline comments, generated via SpecifyKit Plus schemas
- Performance metrics MUST achieve retrieval recall > 90%, with generation coherence scored via human eval or automated metrics

Technology Stack Constraints:
- Cohere API MUST be used for embeddings and generation (no OpenAI allowed)
- Qwen CLI MUST be used for prototyping
- SpecifyKit Plus MUST be used for project specs and workflows
- FastAPI MUST be used for API development
- Neon Serverless Postgres MUST be used for database
- Qdrant Cloud Free Tier MUST be used for vector storage

Resource Constraints:
- Qdrant Free Tier (1GB maximum storage)
- Embeddings MUST be optimized to < 512 dimensions
- Deployment MUST be containerized with Docker
- Deployment MUST be compatible with free tiers (e.g., Render or Vercel for FastAPI)

Allowed Components:
- Backend: FastAPI with Cohere integration
- Database: Neon Serverless Postgres
- Vector Database: Qdrant Cloud Free Tier
- Containerization: Docker
- Orchestration: SpecifyKit Plus for specs/workflows

## Development and Quality Gates

Success Criteria:
- Chatbot MUST accurately answer 95%+ of test queries on book content
- System MUST support selected-text mode without leaking external context
- Chatbot MUST be fully embedded and functional in a sample book viewer (e.g., web/PDF)
- Zero critical bugs MUST be present in production tests
- Code MUST pass review for modularity and security

## Governance

- Constitution supersedes all other project practices and documentation.
- Amendments to this constitution REQUIRE documentation, approval by project maintainers, and a clear migration plan for affected components.
- All code contributions and reviews MUST verify compliance with the principles and standards outlined herein.
- Versioning follows semantic versioning: MAJOR for backward incompatible changes, MINOR for new principles/features, PATCH for clarifications.

**Version**: 1.1.0 | **Ratified**: 2025-12-08 | **Last Amended**: 2025-12-19