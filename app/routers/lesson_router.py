"""
Lesson router — AI lesson and quiz generation.
"""

from fastapi import APIRouter, HTTPException

from app.models.request_models import (
    LessonRequest,
    LessonResponse,
    QuizRequest,
    QuizResponse,
)
from app.services import tutor_service

router = APIRouter(prefix="/api", tags=["lessons"])


@router.post("/lesson", response_model=LessonResponse)
async def generate_lesson(request: LessonRequest):
    """Generate a structured lesson from document content."""
    try:
        lesson = await tutor_service.generate_lesson(
            doc_id=request.doc_id,
            topic=request.topic,
            difficulty=request.difficulty,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return LessonResponse(lesson=lesson)


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate quiz questions from document content."""
    try:
        quiz = await tutor_service.generate_quiz(
            doc_id=request.doc_id,
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found")
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return QuizResponse(quiz=quiz)
