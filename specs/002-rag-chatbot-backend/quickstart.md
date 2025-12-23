# Quickstart: RAG Chatbot Backend

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
   ```

4. **Install requirements.txt**:
   Create the file with required packages:
   ```txt
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   cohere==4.3.1
   qdrant-client==1.7.0
   psycopg2-binary==2.9.9
   python-dotenv==1.0.0
   pydantic==2.5.0
   pytest==7.4.3
   python-multipart==0.0.6
   ```

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Ingest book content**:
   ```bash
   python scripts/ingest_book.py --file path/to/book.txt
   ```

3. **Access the API**:
   - API documentation: http://localhost:8000/docs
   - Health check: GET http://localhost:8000/health

## API Endpoints

### Query Book Content
```
POST /query
```
Request body:
```json
{
  "question": "Your question about the book",
  "selected_text": "Optional selected text for context isolation"
}
```

Response:
```json
{
  "answer": "Generated answer",
  "sources": ["chunk_id_1", "chunk_id_2"],
  "confidence": 0.85
}
```

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T10:00:00Z"
}
```

## Running Tests

```bash
pytest tests/ -v
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
- Embeddings use Cohere's embed-english-v3.0 model with <512 dimensions
- Response time should be under 2 seconds for typical queries
- Selected-text mode strictly isolates context to provided text only