---
id: 0002
title: RAG Chatbot Constitution Update
stage: constitution
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: rag-chatbot
branch: 002-rag-chatbot-backend
user: user
command: /sp.constitution
labels: ["constitution", "rag", "chatbot", "update"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  null
---

## Prompt

```text
Project: Integrated RAG Chatbot Development using SpecifyKit Plus, Qwen CLI, Cohere API, FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier. The chatbot must be embedded within a published book, capable of answering user questions about the book's content, including responses based solely on user-selected text. Core principles:

Accuracy in retrieval and generation through vector-based search and Cohere-powered augmentation
Usability for end-users (intuitive interface, fast response times under 2 seconds)
Modularity (components like retrieval, database, and API loosely coupled for easy maintenance)
Security (API keys encrypted, data privacy compliant with no user data logging)
Excellence in implementation (clean code, optimized performance, multilingual support via Cohere/Qwen) Key standards:
All responses must be grounded in retrieved book content or selected text to minimize hallucinations
Code quality: Follow PEP 8 for Python, with 80%+ test coverage using pytest
Integration testing: End-to-end tests for RAG pipeline using mock data
Documentation: Comprehensive README and inline comments, generated via SpecifyKit Plus schemas
Performance metrics: Retrieval recall > 90%, generation coherence scored via human eval or automated metrics Constraints:
Technologies: Must use Cohere API for embeddings/generation (no OpenAI), Qwen CLI for prototyping, SpecifyKit Plus for project specs/workflows, FastAPI for API, Neon Serverless Postgres for DB, Qdrant Free Tier for vectors
Resource limits: Qdrant Free Tier (1GB max), no paid tiers for initial build; optimize embeddings to < 512 dimensions
Development timeline: Prototype in 1 week, full build in 4 weeks
Deployment: Containerized with Docker, deployable to free tiers (e.g., Render or Vercel for FastAPI) Success criteria:
Chatbot accurately answers 95%+ of test queries on book content
Supports selected-text mode without leaking external context
Fully embedded and functional in a sample book viewer (e.g., web/PDF)
Zero critical bugs in production tests
```

## Response snapshot

The project constitution at .specify/memory/constitution.md was already aligned with the RAG Chatbot Development requirements. The existing constitution (version 1.1.0) already contained the core principles of Accuracy in retrieval and generation, Usability for end-users, Modularity, Security, and Excellence in implementation. It also included the technology stack constraints (Cohere API, Qwen CLI, SpecifyKit Plus, FastAPI, Neon Postgres, Qdrant), resource constraints (free tier limitations), and success criteria (95% accuracy, selected-text mode, embedded functionality). The file was updated with today's date as the last amended date.

## Outcome

- ✅ Impact: Constitution file reviewed and confirmed to match requirements.
- 🧪 Tests: No tests run.
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: None
- 🧠 Reflection: Constitution was already properly configured for the RAG chatbot project.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A