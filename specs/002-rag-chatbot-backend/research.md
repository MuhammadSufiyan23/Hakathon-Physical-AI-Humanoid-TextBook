# Research: RAG Chatbot Backend

## Decision: Technology Stack Selection
**Rationale**: Selected technology stack aligns with project constraints and requirements from constitution. FastAPI provides async capabilities and automatic API documentation. Cohere provides reliable embeddings and generation. Qdrant offers efficient vector search. Neon Postgres provides structured metadata storage with serverless scaling.

**Alternatives considered**:
- OpenAI vs Cohere: Chose Cohere per constitution constraint (no OpenAI)
- Pinecone vs Qdrant: Chose Qdrant per constitution constraint (Qdrant Cloud Free Tier)
- Flask vs FastAPI: Chose FastAPI for better async support and built-in validation

## Decision: Embedding Model Selection
**Rationale**: Cohere embed-english-v3.0 selected as it provides <512 dimensional embeddings to meet resource constraints while offering good semantic understanding for book content. Multilingual capability supports potential future expansion.

**Alternatives considered**:
- embed-english-light-v3.0: Lighter but potentially less accurate for complex book content
- embed-multilingual-v3.0: Supports multiple languages but similar dimensionality to English model

## Decision: Data Chunking Strategy
**Rationale**: 300-500 token chunks with overlap provide optimal balance between context preservation and retrieval efficiency. This size allows for coherent semantic units while maintaining precision in retrieval.

**Alternatives considered**:
- Larger chunks (1000+ tokens): Risk losing precision in retrieval
- Smaller chunks (100-200 tokens): Risk losing context coherence
- No overlap: Risk losing context across chunk boundaries

## Decision: Selected-Text Mode Implementation
**Rationale**: Implement strict context isolation by only passing selected text to generation model, with clear instructions to only use provided context. This prevents leakage from book content when in selected-text mode.

**Alternatives considered**:
- Hybrid approach: Risk of context leakage from book content
- Separate models: Increased complexity without clear benefit

## Decision: API Rate Limiting and Security
**Rationale**: Implement API key-based authentication with rate limiting to prevent abuse while maintaining simplicity. Keys stored securely in environment variables as per constitution.

**Alternatives considered**:
- No authentication: Would violate security requirements
- OAuth2: Overly complex for core functionality, not required by specification
- IP-based limiting: Less flexible than API key approach