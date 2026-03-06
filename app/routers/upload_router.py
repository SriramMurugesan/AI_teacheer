"""
Upload router — PDF upload, document listing, and deletion.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.request_models import DocumentResponse
from app.services import tutor_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF and run the full ingestion pipeline."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        doc_id, num_chunks = await tutor_service.process_document(file)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return DocumentResponse(
        doc_id=doc_id,
        filename=file.filename,
        num_chunks=num_chunks,
        message=f"Successfully processed '{file.filename}' into {num_chunks} chunks",
    )


@router.get("/documents")
async def list_documents():
    """Return all uploaded documents with metadata."""
    return tutor_service.list_documents()


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Remove a document and its vector index."""
    if not tutor_service.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document '{doc_id}' deleted"}
