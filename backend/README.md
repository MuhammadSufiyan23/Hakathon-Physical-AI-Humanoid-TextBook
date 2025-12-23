# RAG Chatbot Backend

A FastAPI-based RAG (Retrieval-Augmented Generation) chatbot backend that allows users to query book content with two modes: full book search and selected-text context isolation.

## Features

- Query book content using RAG methodology
- Two query modes:
  - Full book search: Search across all ingested book content
  - Selected text only: Answer based only on provided text context
- Cohere-powered embeddings and generation
- Qdrant vector database for efficient similarity search
- PostgreSQL for metadata storage
- API key authentication and rate limiting
- Docker containerization

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Access to Cohere API
- Qdrant Cloud account
- Neon Postgres account

## Setup

1. **Clone the repository and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the backend directory with the following:
   ```env
   COHERE_API_KEY=your_cohere_api_key
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=your_neon_postgres_connection_string
   DEBUG=false
   ENVIRONMENT=production
   ```

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Ingest book content**:
   ```bash
   python scripts/ingest_book.py --file path/to/book.txt --title "Book Title" --author "Author Name"
   ```

3. **Access the API**:
   - API documentation: http://localhost:8000/docs
   - Health check: GET http://localhost:8000/api/v1/health

## API Endpoints

### Ingest Content
```
POST /api/v1/ingest
```
Request body:
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "content": "Full book content as text",
  "chunk_size": 500,
  "overlap": 50
}
```

### Query Book Content
```
POST /api/v1/query
```
Request body:
```json
{
  "question": "Your question about the book",
  "selected_text": "Optional selected text for context isolation",
  "mode": "full_book"  // or "selected_text_only"
}
```

### Health Check
```
GET /api/v1/health
```

## Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t rag-chatbot-backend .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 --env-file .env rag-chatbot-backend
   ```

## Configuration Notes

- The system will automatically create necessary collections in Qdrant
- Embeddings use Cohere's embed-english-v3.0 model
- Response time should be under 2 seconds for typical queries
- Selected-text mode strictly isolates context to provided text only
- API keys are required for all endpoints (except health checks)

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

For contract tests specifically:
```bash
pytest tests/contract/ -v
```

For integration tests:
```bash
pytest tests/integration/ -v
```

## Architecture

The backend follows a service-oriented architecture with clear separation of concerns:

- `app/models/` - Pydantic models for request/response validation
- `app/services/` - Business logic for ingestion, retrieval, and generation
- `app/routers/` - API endpoints organized by functionality
- `app/utils/` - Utility functions like text chunking
- `app/middleware/` - Cross-cutting concerns like authentication
- `scripts/` - Standalone scripts for ingestion and other tasks
- `tests/` - Comprehensive test suite organized by type

## Security

- API key authentication required for all endpoints
- Rate limiting to prevent abuse
- Input validation on all endpoints
- Context isolation in selected-text mode
- Environment variables for sensitive data

## Performance

- Response times under 2 seconds for typical queries
- Efficient vector search using Qdrant
- Caching strategies available for high-traffic scenarios
- Optimized for Cohere's <512 dimensional embeddings