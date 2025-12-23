"""
Service for generating answers based on retrieved content
"""
from typing import List, Dict, Any, Optional
from app.services.cohere_client import CohereClient
from app.config import settings
import logging
import time


class GenerationService:
    """
    Service class for generating answers based on retrieved content chunks
    """
    def __init__(self):
        self.cohere_client = CohereClient()
        self.logger = logging.getLogger(__name__)

    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]],
                       max_context_length: int = 2000) -> Dict[str, Any]:
        """
        Generate an answer based on the question and retrieved context chunks.

        Args:
            question: The user's question
            context_chunks: List of relevant context chunks
            max_context_length: Maximum length of context to include

        Returns:
            Dictionary with answer, confidence, and token usage
        """
        try:
            start_time = time.time()

            # Combine context chunks into a single context string
            context_parts = []
            current_length = 0

            for chunk in context_chunks:
                chunk_text = chunk["text"]
                # Check if adding this chunk would exceed the max length
                if current_length + len(chunk_text) > max_context_length:
                    # If adding this chunk would exceed the limit, stop adding chunks
                    break
                context_parts.append(chunk_text)
                current_length += len(chunk_text)

            combined_context = "\n\n".join(context_parts)

            # Generate the answer using Cohere
            answer = self.cohere_client.generate_text(
                prompt=question,
                context=combined_context
            )

            # Calculate response metrics
            tokens_used = len(answer.split())  # Simple token count approximation
            response_time = time.time() - start_time

            # Calculate a basic confidence score based on response quality indicators
            confidence = self._calculate_confidence(answer, context_chunks, response_time)

            return {
                "answer": answer,
                "confidence": confidence,
                "tokens_used": tokens_used
            }

        except Exception as e:
            self.logger.error(f"Error during answer generation: {str(e)}")
            raise e

    def generate_answer_from_context(self, question: str, context: str) -> Dict[str, Any]:
        """
        Generate an answer based on a specific context (used for selected text mode).
        This method ensures strict context isolation by only using the provided context.

        Args:
            question: The user's question
            context: The specific context to use for answering

        Returns:
            Dictionary with answer, confidence, and token usage
        """
        try:
            start_time = time.time()

            # Create a prompt that emphasizes using only the provided context
            # This helps ensure strict context isolation
            isolation_prompt = (
                f"Please answer the following question based ONLY on the provided context. "
                f"Do not use any external knowledge or information beyond what's in the context.\n\n"
                f"Context: {context}\n\n"
                f"Question: {question}\n\n"
                f"If the context does not contain enough information to answer the question, "
                f"please state that explicitly."
            )

            # Generate the answer using only the provided context
            answer = self.cohere_client.generate_text(
                prompt=isolation_prompt,
                context=None  # Explicitly pass no additional context
            )

            # Calculate response metrics
            tokens_used = len(answer.split())  # Simple token count approximation
            response_time = time.time() - start_time

            # Calculate a basic confidence score
            confidence = self._calculate_confidence(answer, [], response_time, is_context_specific=True)

            # Apply post-processing to ensure the answer is properly grounded
            improved_answer = self.improve_answer_quality(answer, question, context)

            return {
                "answer": improved_answer,
                "confidence": confidence,
                "tokens_used": tokens_used
            }

        except Exception as e:
            self.logger.error(f"Error during context-specific answer generation: {str(e)}")
            raise e

    def _calculate_confidence(self, answer: str, context_chunks: List[Dict[str, Any]],
                            response_time: float, is_context_specific: bool = False) -> float:
        """
        Calculate a basic confidence score based on various factors.

        Args:
            answer: The generated answer
            context_chunks: The context chunks used to generate the answer
            response_time: Time taken to generate the answer
            is_context_specific: Whether this is for context-specific generation

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Start with a base confidence
        confidence = 0.5

        # Increase confidence if we have good context
        if context_chunks:
            avg_score = sum(chunk.get("score", 0) for chunk in context_chunks) / len(context_chunks)
            # Adjust confidence based on the average relevance score of context chunks
            confidence += (avg_score * 0.3)  # Max +0.3 for good context

        # Adjust based on answer length (very short answers might be low confidence)
        if len(answer.strip()) < 10:
            confidence -= 0.2
        elif len(answer.strip()) > 50:  # Longer, more detailed answers
            confidence += 0.1

        # Adjust based on response time (very fast responses might not be well-considered)
        if response_time < 0.1:  # Less than 100ms might be too fast
            confidence -= 0.1

        # For context-specific generation, we might have higher confidence
        if is_context_specific:
            confidence += 0.1

        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))

    def validate_generation_input(self, question: str, context: Optional[str] = None) -> bool:
        """
        Validate input for generation.

        Args:
            question: The question to validate
            context: The context to validate (optional)

        Returns:
            True if input is valid, False otherwise
        """
        if not question or len(question.strip()) < 1:
            return False

        if context is not None and len(context) > 10000:  # Context too long
            return False

        return True

    def format_sources(self, context_chunks: List[Dict[str, Any]], max_sources: int = 5) -> List[Dict[str, Any]]:
        """
        Format context chunks into source references for the response.

        Args:
            context_chunks: List of context chunks
            max_sources: Maximum number of sources to include

        Returns:
            List of formatted source references
        """
        sources = []
        for chunk in context_chunks[:max_sources]:
            source = {
                "chunk_id": chunk.get("id", ""),
                "text_snippet": chunk.get("text", "")[:200] + "..." if len(chunk.get("text", "")) > 200 else chunk.get("text", ""),
                "relevance_score": chunk.get("score", 0.0)
            }
            sources.append(source)

        return sources

    def improve_answer_quality(self, answer: str, question: str, context: str) -> str:
        """
        Apply post-processing to improve answer quality.

        Args:
            answer: The generated answer
            question: The original question
            context: The context used for generation

        Returns:
            Improved answer
        """
        # Basic post-processing to ensure the answer addresses the question
        if "does not contain" in answer.lower() or "no information" in answer.lower():
            # If the system couldn't find relevant info, make that clear
            return answer
        else:
            # Ensure the answer is coherent and relevant
            return answer.strip()


# Singleton instance
generation_service = GenerationService()