"""
Cohere API client wrapper for embeddings and generation
Updated for Cohere Chat API (post-September 2025)
"""
import cohere
from typing import List, Dict, Any, Optional
from app.config import settings


class CohereClient:
    """
    Wrapper for Cohere API functionality
    """
    def __init__(self):
        self.client = cohere.Client(api_key=settings.cohere_api_key)
        # Embedding model - v3.0 gives 1024 dimensions
        self.embedding_model = "embed-english-v3.0"
        # Generation model - use command-r-plus or command-r
        self.generation_model = "command-r-08-2024"

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        response = self.client.embed(
            texts=texts,
            model=self.embedding_model,
            input_type="search_document"  # appropriate for document search
        )
        return [embedding for embedding in response.embeddings]

    def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text based on a prompt and optional context using the new Chat API

        Args:
            prompt: The user's question or prompt
            context: Optional context to ground the response

        Returns:
            Generated text response
        """
        if context:
            message = f"""Context:
{context}

Question: {prompt}

Instructions:
- Answer ONLY based on the provided context.
- If the context does not contain enough information to answer the question, say "I don't have enough information from the book to answer this."
- Be concise and helpful.
- Do not add external knowledge."""
        else:
            message = prompt

        try:
            response = self.client.chat(
                model=self.generation_model,
                message=message,
                max_tokens=500,
                temperature=0.3,
                preamble="You are a helpful assistant that answers questions about the book using only the provided context."
            )
            return response.text.strip()
        except Exception as e:
            return f"Generation error: {str(e)}"

    def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to query

        Args:
            query: The search query
            documents: List of documents to rerank
            top_n: Number of top results to return

        Returns:
            List of reranked documents with indices and relevance scores
        """
        try:
            response = self.client.rerank(
                model="rerank-english-v3.0",  # Updated to v3 if available, or keep v2.0
                query=query,
                documents=documents,
                top_n=top_n
            )
            return [
                {
                    "index": r.index,
                    "relevance_score": r.relevance_score,
                    "text": r.document["text"] if isinstance(r.document, dict) else str(r.document)
                }
                for r in response.results
            ]
        except Exception as e:
            print(f"Rerank error: {e}")
            # Fallback: return original order
            return [{"index": i, "relevance_score": 0.0, "text": doc} for i, doc in enumerate(documents)]


# Singleton instance
cohere_client = CohereClient()