"""
RAG (Retrieval-Augmented Generation) service for FAR chatbot.

Handles semantic search, context formatting, and OpenAI response generation.
"""

from typing import List, Dict, Any, Optional
import time
import re

from openai import OpenAI

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings


class RAGService:
    """Manages RAG pipeline for question answering."""

    SECTION_PATTERN = re.compile(r'\b(\d{1,2}\.\d{1,3}(?:-\d{1,3})?)\b')
    FALLBACK_SCORE_THRESHOLD = 0.0  # Used when initial search returns nothing

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """Get OpenAI client instance."""
        return OpenAI(api_key=settings.openai_api_key)

    @classmethod
    def retrieve_context(
        cls,
        query: str,
        max_chunks: int = 5,
        chapter_filter: Optional[int] = None,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant FAR content chunks for a query.

        Args:
            query: User's question
            max_chunks: Maximum number of chunks to retrieve
            chapter_filter: Optional chapter number to filter by
            score_threshold: Minimum similarity score (0-1)

        Returns:
            Dictionary containing retrieved chunks and fallback details
        """
        # Generate query embedding once
        query_embedding = EmbeddingsService.generate_embedding(query)

        def _make_result(
            chunks: List[Dict[str, Any]],
            fallback_used: bool,
            threshold_used: float,
            fallback_threshold: Optional[float]
        ) -> Dict[str, Any]:
            return {
                "chunks": chunks,
                "fallback_used": fallback_used,
                "initial_threshold": threshold_used,
                "fallback_threshold": fallback_threshold
            }

        # If the question explicitly references FAR sections, try to scope the search.
        section_refs = cls.SECTION_PATTERN.findall(query)
        if section_refs:
            for section_id in section_refs:
                targeted_results = VectorStoreService.search(
                    query_vector=query_embedding,
                    limit=max_chunks,
                    chapter_filter=chapter_filter,
                    section_value=section_id,
                    score_threshold=0.0  # allow all results when filtering by section
                )
                if targeted_results:
                    return _make_result(
                        chunks=targeted_results,
                        fallback_used=False,
                        threshold_used=0.0,
                        fallback_threshold=None
                    )

        # Search vector database
        results = VectorStoreService.search(
            query_vector=query_embedding,
            limit=max_chunks,
            chapter_filter=chapter_filter,
            score_threshold=score_threshold
        )

        if results:
            return _make_result(
                chunks=results,
                fallback_used=False,
                threshold_used=score_threshold,
                fallback_threshold=None
            )

        # Try again with a much lower threshold before giving up completely.
        fallback_results = VectorStoreService.search(
            query_vector=query_embedding,
            limit=max_chunks,
            chapter_filter=chapter_filter,
            score_threshold=cls.FALLBACK_SCORE_THRESHOLD
        )

        return _make_result(
            chunks=fallback_results,
            fallback_used=True,
            threshold_used=score_threshold,
            fallback_threshold=cls.FALLBACK_SCORE_THRESHOLD
        )

    @classmethod
    def format_context(cls, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context string for prompt.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant FAR content found."

        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            payload = chunk["payload"]
            score = chunk["score"]

            # Support both 'text' and 'content' field names for backward compatibility
            text_content = payload.get('text') or payload.get('content', '')

            # Support different metadata field names
            section_info = payload.get('section') or payload.get('file', 'Unknown')

            context_parts.append(
                f"[Source {i}] FAR Section {section_info} (Relevance: {score:.2f})\n"
                f"{text_content}\n"
            )

        return "\n---\n\n".join(context_parts)

    @classmethod
    def generate_response(
        cls,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        selected_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response using OpenAI Chat Completions API.

        Args:
            query: User's question
            context: Retrieved FAR content
            conversation_history: Optional previous messages
            selected_text: Optional text selected by user

        Returns:
            Dictionary with response, sources, and metadata
        """
        start_time = time.time()

        # Build system message
        system_message = """You are an expert AI assistant specializing in the Federal Acquisition Regulation (FAR).

Your role is to:
1. Answer questions accurately based on the provided FAR content
2. Cite specific FAR sections when providing information
3. Explain complex procurement regulations in clear, accessible language
4. Acknowledge when information is not in the provided context

Guidelines:
- Only use information from the provided FAR sections
- Always cite section numbers when referencing regulations
- If the context contains any FAR excerpts, you must answer using them.
- Only say that no relevant information exists when the context literally says "No relevant FAR content found."
- Be concise but complete in your explanations
- Use professional but friendly tone"""

        # Build user message
        user_parts = []

        if selected_text:
            user_parts.append(f"I've selected this text from the FAR:\n\"{selected_text}\"\n")

        user_parts.append(f"Question: {query}\n")
        user_parts.append(f"\n===FAR CONTEXT===\n{context}\n===END CONTEXT===")

        user_message = "\n".join(user_parts)

        # Build messages array
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current query
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI API
        client = cls.get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # Extract response
        assistant_message = response.choices[0].message.content
        token_count = response.usage.total_tokens

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "content": assistant_message,
            "token_count": token_count,
            "processing_time_ms": processing_time_ms
        }

    @classmethod
    def process_query(
        cls,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        selected_text: Optional[str] = None,
        chapter_filter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline: retrieve context and generate response.

        Args:
            query: User's question
            conversation_history: Optional conversation history
            selected_text: Optional selected text
            chapter_filter: Optional chapter filter

        Returns:
            Dictionary with response, sources, and metadata
        """
        # Retrieve relevant context
        retrieval = cls.retrieve_context(
            query=query,
            max_chunks=settings.max_chunk_retrieval,
            chapter_filter=chapter_filter
        )
        chunks = retrieval["chunks"]

        # Format context
        context = cls.format_context(chunks)

        fallback_note: Optional[str] = None
        if retrieval["fallback_used"]:
            if chunks:
                fallback_note = (
                    "I couldn't find an exact FAR passage matching that question, "
                    "so I'm sharing the closest related sections."
                )
            else:
                fallback_note = (
                    "I couldn't find any FAR passages that match that question, "
                    "even after broadening the search."
                )

        # Generate response
        response_data = cls.generate_response(
            query=query,
            context=context,
            conversation_history=conversation_history,
            selected_text=selected_text
        )
        final_content = response_data["content"]
        if fallback_note:
            final_content = f"{fallback_note}\n\n{final_content}"

        # Format sources for frontend
        sources = []
        for chunk in chunks:
            payload = chunk["payload"]
            # Support both 'text' and 'content' field names
            text_content = payload.get('text') or payload.get('content', '')
            sources.append({
                "chunk_id": str(chunk["id"]),
                "chapter": payload.get("chapter", 1),
                "section": payload.get("section", ""),
                "page": payload.get("page"),
                "relevance_score": chunk["score"],
                "excerpt": text_content[:200]  # First 200 chars
            })

        return {
            "content": final_content,
            "sources": sources,
            "token_count": response_data["token_count"],
            "processing_time_ms": response_data["processing_time_ms"]
        }
