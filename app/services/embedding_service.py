"""
Embedding service — lazy-loaded SentenceTransformer singleton.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config.settings import get_settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (downloaded on first use)."""
    global _model
    if _model is None:
        settings = get_settings()
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def get_embeddings(texts: list[str]) -> np.ndarray:
    """
    Batch-encode a list of texts into embedding vectors.

    Returns
    -------
    np.ndarray
        Shape (len(texts), embedding_dim).
    """
    model = _get_model()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)


def get_query_embedding(query: str) -> np.ndarray:
    """
    Encode a single query string.

    Returns
    -------
    np.ndarray
        Shape (1, embedding_dim) — ready for FAISS search.
    """
    model = _get_model()
    embedding = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    return np.array(embedding, dtype=np.float32)
