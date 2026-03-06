"""
PDF processing service — async file saving and text extraction.
"""

import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from pypdf import PdfReader

from app.config.settings import get_settings


async def save_upload(file: UploadFile) -> tuple[str, Path]:
    """
    Stream-save an uploaded PDF and return (doc_id, file_path).
    Uses aiofiles for non-blocking I/O.
    """
    settings = get_settings()
    settings.upload_path.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4().hex[:12]
    safe_name = f"{doc_id}_{file.filename}"
    file_path = settings.upload_path / safe_name

    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 64):  # 64 KB chunks
            await out.write(chunk)

    return doc_id, file_path


def extract_text(file_path: Path) -> str:
    """
    Extract all text from a PDF file.
    Returns concatenated text from every page.
    """
    reader = PdfReader(str(file_path))
    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)
