"""
Pydantic request / response models for the API.
"""

from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    doc_id: str = Field(..., description="Document identifier returned from upload")
    question: str = Field(..., min_length=1, description="Student's question")


class LessonRequest(BaseModel):
    doc_id: str
    topic: str = Field("", description="Optional topic focus; uses full doc if empty")
    difficulty: str = Field("beginner", description="beginner | intermediate | advanced")


class QuizRequest(BaseModel):
    doc_id: str
    topic: str = Field("", description="Optional topic focus")
    num_questions: int = Field(5, ge=1, le=20)
    difficulty: str = Field("beginner", description="beginner | intermediate | advanced")


# ── Responses ─────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list, description="Retrieved context chunks")


class LessonResponse(BaseModel):
    lesson: str


class QuizResponse(BaseModel):
    quiz: str


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    documents_loaded: int
