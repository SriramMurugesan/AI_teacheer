"""
Tutor service — orchestrates the full RAG pipeline.
Wires PDF → chunks → embeddings → vector store → LLM.
"""

from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import UploadFile

from app.services.pdf_service import save_upload, extract_text
from app.services.chunk_service import chunk_text
from app.services.embedding_service import get_embeddings, get_query_embedding
from app.services.vector_service import vector_store
from app.services.llm_service import llm_service
from app.utils.prompts import TUTOR_PROMPT, LESSON_PROMPT, QUIZ_PROMPT

# Max words per chunk to keep prompts manageable for local LLMs
_MAX_CONTEXT_WORDS = 1500


def _build_context(chunks: list[str], max_words: int = _MAX_CONTEXT_WORDS) -> str:
    """Join chunks into context, truncating to max_words total."""
    context_parts = []
    word_count = 0
    for chunk in chunks:
        words = chunk.split()
        if word_count + len(words) > max_words:
            remaining = max_words - word_count
            if remaining > 0:
                context_parts.append(" ".join(words[:remaining]))
            break
        context_parts.append(chunk)
        word_count += len(words)
    return "\n\n".join(context_parts)

# ── In-memory document metadata ──────────────────────────────
_doc_metadata: dict[str, dict] = {}  # doc_id → {filename, file_path}


# ── Document Ingestion ───────────────────────────────────────

async def process_document(file: UploadFile) -> tuple[str, int]:
    """
    Full ingestion pipeline:
    1. Save uploaded PDF
    2. Extract text
    3. Chunk text
    4. Create embeddings
    5. Store in vector DB

    Returns (doc_id, num_chunks).
    """
    # Step 1 — Save
    doc_id, file_path = await save_upload(file)

    # Step 2 — Extract
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError("Could not extract any text from the PDF")

    # Step 3 — Chunk
    chunks = chunk_text(text)

    # Step 4 — Embed
    embeddings = get_embeddings(chunks)

    # Step 5 — Store
    vector_store.add_document(doc_id, chunks, embeddings)

    # Metadata
    _doc_metadata[doc_id] = {
        "filename": file.filename,
        "file_path": str(file_path),
    }

    return doc_id, len(chunks)


# ── RAG Q&A ──────────────────────────────────────────────────

async def ask_question(doc_id: str, question: str) -> tuple[str, list[str]]:
    """
    RAG pipeline:
    1. Embed the question
    2. Retrieve similar chunks
    3. Build prompt with context
    4. Get LLM response

    Returns (answer, source_chunks).
    """
    # Retrieve
    query_emb = get_query_embedding(question)
    relevant_chunks = vector_store.search(doc_id, query_emb)

    context = _build_context(relevant_chunks)

    # Generate
    prompt = TUTOR_PROMPT.format(context=context, question=question)
    answer = await llm_service.generate(prompt)

    return answer, relevant_chunks


async def stream_answer(doc_id: str, question: str) -> AsyncGenerator[str, None]:
    """Streaming RAG — yields tokens as they arrive."""
    query_emb = get_query_embedding(question)
    relevant_chunks = vector_store.search(doc_id, query_emb)
    context = _build_context(relevant_chunks)

    prompt = TUTOR_PROMPT.format(context=context, question=question)

    async for token in llm_service.stream(prompt):
        yield token


# ── Lesson Generation ────────────────────────────────────────

async def generate_lesson(
    doc_id: str,
    topic: str = "",
    difficulty: str = "beginner",
) -> str:
    """Generate a structured lesson from the document content."""
    if topic:
        query_emb = get_query_embedding(topic)
        chunks = vector_store.search(doc_id, query_emb, top_k=5)
    else:
        chunks = vector_store.get_all_chunks(doc_id)[:5]

    context = _build_context(chunks)
    topic_text = topic if topic else "General overview of the document"

    prompt = LESSON_PROMPT.format(
        context=context, topic=topic_text, difficulty=difficulty
    )
    return await llm_service.generate(prompt)


# ── Quiz Generation ──────────────────────────────────────────

async def generate_quiz(
    doc_id: str,
    topic: str = "",
    num_questions: int = 5,
    difficulty: str = "beginner",
) -> str:
    """Generate quiz questions from the document content."""
    if topic:
        query_emb = get_query_embedding(topic)
        chunks = vector_store.search(doc_id, query_emb, top_k=3)
    else:
        chunks = vector_store.get_all_chunks(doc_id)[:3]

    context = _build_context(chunks)
    topic_text = topic if topic else "General topics from the document"

    prompt = QUIZ_PROMPT.format(
        context=context,
        topic=topic_text,
        num_questions=num_questions,
        difficulty=difficulty,
    )
    return await llm_service.generate(prompt)


# ── Helpers ──────────────────────────────────────────────────

def get_document_metadata(doc_id: str) -> dict | None:
    return _doc_metadata.get(doc_id)


def list_documents() -> list[dict]:
    """Return metadata for all loaded documents."""
    docs = []
    for doc_id in vector_store.list_documents():
        meta = _doc_metadata.get(doc_id, {})
        docs.append({
            "doc_id": doc_id,
            "filename": meta.get("filename", "unknown"),
            "num_chunks": vector_store.document_chunk_count(doc_id),
        })
    return docs


def delete_document(doc_id: str) -> bool:
    """Remove a document from the store and metadata."""
    _doc_metadata.pop(doc_id, None)
    return vector_store.delete_document(doc_id)
