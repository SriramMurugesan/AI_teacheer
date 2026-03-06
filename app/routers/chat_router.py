"""
Chat router — RAG-based Q&A with regular and streaming modes.
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.request_models import ChatRequest, ChatResponse
from app.services import tutor_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question against an uploaded document (RAG)."""
    try:
        answer, sources = await tutor_service.ask_question(
            request.doc_id, request.question
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return ChatResponse(answer=answer, sources=sources)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream a RAG answer via Server-Sent Events."""
    try:
        # Verify document exists first
        from app.services.vector_service import vector_store
        if request.doc_id not in vector_store.list_documents():
            raise HTTPException(status_code=404, detail="Document not found")
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")

    async def event_generator():
        try:
            async for token in tutor_service.stream_answer(
                request.doc_id, request.question
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
