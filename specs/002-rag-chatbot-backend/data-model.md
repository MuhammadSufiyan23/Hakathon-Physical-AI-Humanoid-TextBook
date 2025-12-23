# Data Model: RAG Chatbot Backend

## Entities

### Book Content
**Description**: Represents the digital book material that has been ingested
**Fields**:
- id: UUID (primary key)
- title: string (book title)
- author: string (book author)
- content_chunks: array of ContentChunk objects
- metadata: JSON object (additional book information)

### ContentChunk
**Description**: Represents a segment of book content that has been processed and embedded
**Fields**:
- id: UUID (primary key)
- book_id: UUID (foreign key to Book Content)
- text: string (the actual text content)
- embedding: vector (Cohere embedding vector)
- page_number: integer (original page location, optional)
- chapter: string (original chapter title, optional)
- chunk_index: integer (sequence within book)
- metadata: JSON object (additional chunk-specific information)

### QueryRequest
**Description**: Represents a user's query to the system
**Fields**:
- question: string (the user's question)
- selected_text: string (optional selected text context)
- mode: enum (full_book | selected_text_only)
- metadata: JSON object (request metadata)

### Response
**Description**: Represents the AI-generated answer from the system
**Fields**:
- answer: string (the generated answer)
- sources: array of UUIDs (references to ContentChunk IDs used)
- confidence: float (0-1 confidence score)
- tokens_used: integer (number of tokens in response)

### APIKey
**Description**: Represents API keys for authentication and rate limiting
**Fields**:
- key: string (hashed API key)
- name: string (description of key purpose)
- rate_limit: integer (requests per minute allowed)
- created_at: timestamp
- last_used: timestamp (optional)

## Relationships

- Book Content (1) → (many) ContentChunk
- ContentChunk (many) → (many) QueryRequest (through semantic similarity)
- QueryRequest (1) → (1) Response

## Validation Rules

- ContentChunk.text must be between 100 and 1000 characters
- Book Content must have a unique title/author combination
- QueryRequest.question must not be empty
- APIKey.key must be unique and properly hashed
- Embedding vectors must have <512 dimensions

## State Transitions

- Book Content: draft → ingested → indexed → available
- QueryRequest: received → processing → completed → responded
- APIKey: created → active → suspended (if rate limit exceeded)