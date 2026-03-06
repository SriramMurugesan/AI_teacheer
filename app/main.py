"""
AI PDF Tutor — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.models.request_models import HealthResponse
from app.routers import upload_router, chat_router, lesson_router
from app.services.llm_service import llm_service
from app.services.vector_service import vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    settings = get_settings()

    # Startup — ensure upload directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    print(f"🚀 AI PDF Tutor started | LLM: {settings.LLM_PROVIDER}")
    print(f"📁 Uploads: {settings.upload_path.resolve()}")

    yield

    # Shutdown — cleanup resources
    await llm_service.close()
    print("👋 AI PDF Tutor shutdown complete")


# ── App Instance ─────────────────────────────────────────────

app = FastAPI(
    title="AI PDF Tutor",
    description="RAG-powered AI tutor that teaches from your PDFs",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────

app.include_router(upload_router.router)
app.include_router(chat_router.router)
app.include_router(lesson_router.router)


# ── Health Check ─────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        llm_provider=settings.LLM_PROVIDER,
        documents_loaded=vector_store.total_documents,
    )
