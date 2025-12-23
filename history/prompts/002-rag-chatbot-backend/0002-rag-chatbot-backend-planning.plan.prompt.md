---
id: 0002
title: RAG Chatbot Backend Planning
stage: plan
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-chatbot-backend
branch: 002-rag-chatbot-backend
user: user
command: /sp.plan
labels: ["plan", "rag", "chatbot", "backend"]
links:
  spec: specs/002-rag-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-chatbot-backend/plan.md
  - specs/002-rag-chatbot-backend/research.md
  - specs/002-rag-chatbot-backend/data-model.md
  - specs/002-rag-chatbot-backend/quickstart.md
  - specs/002-rag-chatbot-backend/contracts/api-contract.yaml
tests:
  null
---

## Prompt

```text
Project Plan: Integrated RAG Chatbot Backend Development (Strictly within existing "backend" folder)

Phase 1: Setup and Configuration (Days 1-2)
- Create .env file inside backend/ root for all credentials (never commit to git)
  COHERE_API_KEY=91TCPoZqUmyLkhtqZnnzR0mSezzlfRXaMgwy4zu1
  QDRANT_URL=https://afcd9119-6ed1-4195-87b1-0e1fc94a1ae7.eu-west-2-0.aws.cloud.qdrant.io/
  QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.w0WuOCsRTJZnQZ1Y3le4ect8QLkyloCP2PPJBYU5o6U
  DATABASE_URL=postgresql://neondb_owner:npg_3KsHFmVEa5lB@ep-hidden-truth-ablhtq3f-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
- Install required packages in backend/ (create requirements.txt)
  fastapi, uvicorn, cohere, qdrant-client, psycopg2-binary, python-dotenv, langchain (optional for helpers), pydantic, pytest
- Setup basic project structure inside backend/
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py          # FastAPI app entry
  │   ├── routers/         # API endpoints
  │   ├── services/        # RAG logic, retrieval, generation
  │   ├── models/          # Pydantic schemas
  │   └── utils/           # Helpers (embedding, chunking)
  ├── scripts/
  │   └── ingest_book.py   # Script to chunk and upload book content
  ├── tests/
  │   └── test_rag.py
  ├── .env
  ├── requirements.txt
  └── Dockerfile

Phase 2: Data Ingestion Pipeline (Days 3-5)
- Write scripts/ingest_book.py
  - Load book text (from provided .txt or PDF in backend/data/ if any)
  - Chunk text into 300-500 token chunks with overlap
  - Generate embeddings using Cohere embed-english-v3.0 (or multilingual if needed)
  - Upsert vectors + metadata into Qdrant collection "book_content"
  - Store chunk metadata (page/chapter) in Neon Postgres table "chunks"
- Run locally with Qwen CLI to test chunking logic before Cohere calls
- Ensure total vectors fit within Qdrant Free Tier (~1GB limit)

Phase 3: RAG Core Services (Days 6-10)
- Implement services/retrieval.py
  - Hybrid search in Qdrant (vector + optional keyword)
  - Optional reranking with Cohere rerank endpoint
- Implement services/generation.py
  - Prompt templates for two modes:
    1. Full book query
    2. Selected-text only (strict context isolation)
  - Use Cohere chat/completion for generation
  - Enforce grounding: "Answer only based on provided context"
- Add caching layer (simple Redis or in-memory for prototype)

Phase 4: FastAPI Endpoints (Days 11-14)
- Create routers/chat.py with endpoints:
  POST /query            # {question: str, selected_text: str (optional)}
  POST /ingest           # Trigger re-ingestion (admin only in future)
  GET  /health
- Response format: {answer: str, sources: [chunk_ids or text snippets]}
- Input validation with Pydantic models

Phase 5: Testing & Optimization (Days 15-20)
- Write comprehensive pytest suite in tests/
  - Unit tests for chunking, embedding
  - Integration tests for retrieval accuracy
  - End-to-end tests with mock queries
- Manual testing with Qwen CLI for prompt refinement
- Optimize: reduce latency (<2s), minimize token usage, ensure <512 dim embeddings
- Test selected-text mode isolation rigorously

Phase 6: Dockerization & Documentation (Days 21-28)
- Write Dockerfile (multi-stage, lightweight)
- Update README.md in backend/ with:
  - Setup instructions
  - API documentation (Swagger auto-gen)
  - Embedding instructions for frontend
  - Environment variables list
- Final security check: no hard-coded keys, .env in .gitignore

Deliverables (All inside backend/ folder):
- Fully functional FastAPI RAG backend
- Ingested book content in Qdrant + Postgres
- Tested endpoints ready for frontend embedding
- Docker support for deployment
- 80%+ test coverage

Milestones:
Week 1: Environment setup + ingestion script complete
Week 2: RAG services + basic API endpoints
Week 3: Testing + optimization
Week 4: Docker + documentation + final validation
```

## Response snapshot

Created the implementation plan for the RAG Chatbot Backend feature. Generated the following artifacts in specs/002-rag-chatbot-backend/:
- plan.md: Implementation plan with technical context, constitution check, and project structure
- research.md: Research document with technology decisions and rationale
- data-model.md: Data model defining entities, relationships, and validation rules
- quickstart.md: Quickstart guide with setup and usage instructions
- contracts/api-contract.yaml: OpenAPI contract for the API endpoints

All artifacts align with the constitution requirements and the detailed project plan provided by the user.

## Outcome

- ✅ Impact: Implementation plan and supporting artifacts created.
- 🧪 Tests: No tests run.
- 📁 Files: specs/002-rag-chatbot-backend/plan.md, research.md, data-model.md, quickstart.md, contracts/api-contract.yaml
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Planning phase completed with comprehensive documentation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A