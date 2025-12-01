"""
RAG (Retrieval-Augmented Generation) service for FAR chatbot.

Handles semantic search, context formatting, and OpenAI response generation.
"""

from typing import List, Dict, Any, Optional
import time
import re
from pathlib import Path

from openai import OpenAI

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.services.text_chunker import TextChunker


class RAGService:
    """Manages RAG pipeline for question answering."""

    SECTION_PATTERN = re.compile(r'\b(\d{1,2}\.\d{1,3}(?:-\d{1,3})?)\b')
    DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """Get OpenAI client instance."""
        return OpenAI(api_key=settings.openai_api_key)

    @classmethod
    def _extract_section_references(cls, query: str) -> List[str]:
        """Find FAR section identifiers mentioned explicitly in the query."""
        if not query:
            return []

        matches = cls.SECTION_PATTERN.findall(query)
        # Preserve order while deduplicating
        seen = set()
        sections: List[str] = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                sections.append(match)
        return sections

    @classmethod
    def _strip_front_matter(cls, content: str) -> str:
        """Remove YAML front matter from markdown text if present."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content.strip()

    @classmethod
    def _load_section_chunks(cls, section_id: str) -> List[Dict[str, Any]]:
        """Load markdown content for a FAR section directly from docs."""
        if not cls.DOCS_DIR.exists():
            return []

        part_number = section_id.split('.', 1)[0]
        file_path = cls.DOCS_DIR / f"part-{part_number}" / f"{section_id}.md"

        if not file_path.exists():
            return []

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return []

        text = cls._strip_front_matter(content)
        if not text:
            return []

        chunks = TextChunker.chunk_text(text)
        if not chunks:
            return []

        payloads: List[Dict[str, Any]] = []
        chapter = int(part_number)

        for idx, chunk in enumerate(chunks):
            payloads.append({
                "id": f"section-{section_id}-{idx}",
                "score": 0.99,
                "payload": {
                    "text": chunk,
                    "chapter": chapter,
                    "section": section_id,
                    "source_file": str(file_path),
                    "chunk_index": idx
                }
            })

        return payloads

    @classmethod
    def retrieve_context(
        cls,
        query: str,
        max_chunks: int = 5,
        chapter_filter: Optional[int] = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant FAR content chunks for a query.

        Args:
            query: User's question
            max_chunks: Maximum number of chunks to retrieve
            chapter_filter: Optional chapter number to filter by
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of retrieved chunks with metadata
        """
        # Prefer direct section lookups when a FAR citation is explicitly referenced
        section_refs = cls._extract_section_references(query)
        direct_chunks: List[Dict[str, Any]] = []
        for section_id in section_refs:
            direct_chunks.extend(cls._load_section_chunks(section_id))
            if len(direct_chunks) >= max_chunks:
                break

        if direct_chunks:
            return direct_chunks[:max_chunks]

        # Generate query embedding
        query_embedding = EmbeddingsService.generate_embedding(query)

        # Search vector database
        results = VectorStoreService.search(
            query_vector=query_embedding,
            limit=max_chunks,
            chapter_filter=chapter_filter,
            score_threshold=score_threshold
        )

        return results

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
- If the answer isn't in the provided context, say so clearly
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
        chunks = cls.retrieve_context(
            query=query,
            max_chunks=settings.max_chunk_retrieval,
            chapter_filter=chapter_filter
        )

        # Format context
        context = cls.format_context(chunks)

        # Generate response
        response_data = cls.generate_response(
            query=query,
            context=context,
            conversation_history=conversation_history,
            selected_text=selected_text
        )

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
            "content": response_data["content"],
            "sources": sources,
            "token_count": response_data["token_count"],
            "processing_time_ms": response_data["processing_time_ms"]
        }
