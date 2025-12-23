

"""
Main service for handling book content queries
"""
from typing import Dict, Any, List, Optional
from app.services.retrieval_service import retrieval_service  # Use Cohere-based singleton
from app.services.generation_service import GenerationService
from app.models.request import QueryMode
import logging
import time


class QueryService:
    """
    Main service class for handling book content queries with different modes
    """
    def __init__(self):
        self.retrieval_service = retrieval_service
        self.generation_service = GenerationService()
        self.logger = logging.getLogger(__name__)

    def query_book_content(self, question: str, selected_text: Optional[str] = None,
                           mode: QueryMode = QueryMode.FULL_BOOK, book_id: Optional[str] = None,
                           max_chunks: int = 5) -> Dict[str, Any]:
        """
        Main method to query book content based on the specified mode.
        NOTE: This method is now fully synchronous to avoid asyncio.wait_for timeout issues.
        """
        try:
            start_time = time.time()

            # Validate inputs
            if not question or len(question.strip()) < 1:
                raise ValueError("Question cannot be empty")

            if mode == QueryMode.SELECTED_TEXT_ONLY and not selected_text:
                raise ValueError("Selected text is required for selected_text_only mode")

            # Retrieve context chunks based on mode
            if mode == QueryMode.FULL_BOOK:
                context_chunks = self._perform_full_book_search(question, book_id, max_chunks)
            else:  # SELECTED_TEXT_ONLY
                context_chunks = self._perform_selected_text_search(selected_text, question)

            # Generate answer based on retrieved context
            if mode == QueryMode.SELECTED_TEXT_ONLY:
                generation_result = self.generation_service.generate_answer_from_context(
                    question=question,
                    context=selected_text
                )
            else:
                generation_result = self.generation_service.generate_answer(
                    question=question,
                    context_chunks=context_chunks
                )

            # Format the sources
            sources = self.generation_service.format_sources(context_chunks)

            # Prepare final response
            response = {
                "answer": generation_result.get("answer", "No answer generated."),
                "sources": sources,
                "confidence": round(generation_result.get("confidence", 0.0), 2),
                "tokens_used": generation_result.get("tokens_used", 0),
                "response_time": round(time.time() - start_time, 2)
            }

            # Log successful query
            self.logger.info(
                f"Query completed successfully. Mode: {mode}, "
                f"Response time: {response['response_time']}s, "
                f"Confidence: {response['confidence']}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error during query processing: {str(e)}")
            raise e

    def _perform_full_book_search(self, question: str, book_id: Optional[str], max_chunks: int) -> List[Dict[str, Any]]:
        retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(
            query=question,
            book_id=book_id,
            limit=max_chunks
        )

        reranked_chunks = self.retrieval_service.rerank_results(
            query=question,
            chunks=retrieved_chunks,
            top_n=max_chunks
        )

        return reranked_chunks

    def _perform_selected_text_search(self, selected_text: str, question: str) -> List[Dict[str, Any]]:
        chunks = self.retrieval_service.retrieve_by_selected_text(
            selected_text=selected_text,
            question=question
        )

        for chunk in chunks:
            if chunk.get("text", "") != selected_text:
                self.logger.warning("Context isolation may have been compromised in selected text mode")

        return chunks

    def validate_query_params(self, question: str, mode: QueryMode, selected_text: Optional[str] = None) -> bool:
        if not question or len(question.strip()) < 1:
            return False

        if mode == QueryMode.SELECTED_TEXT_ONLY and (not selected_text or len(selected_text.strip()) < 1):
            return False

        if mode not in [QueryMode.FULL_BOOK, QueryMode.SELECTED_TEXT_ONLY]:
            return False

        return True

    def get_query_statistics(self) -> Dict[str, Any]:
        return {
            "total_queries": 0,
            "avg_response_time": 0.0,
            "avg_confidence": 0.0,
            "successful_queries": 0,
            "failed_queries": 0
        }

    def check_query_limits(self, user_id: Optional[str] = None) -> bool:
        return True


# Singleton instance
query_service = QueryService()