"""
Vector store service — per-document FAISS index management.
"""

import faiss
import numpy as np

from app.config.settings import get_settings


class VectorStore:
    """
    Manages one FAISS index per uploaded document.
    Stores chunk text alongside the index for retrieval.
    """

    def __init__(self) -> None:
        # doc_id → (faiss.Index, list[str])
        self._stores: dict[str, tuple[faiss.Index, list[str]]] = {}

    # ── Write ────────────────────────────────────────────────

    def add_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: np.ndarray,
    ) -> None:
        """Create a FAISS index for a document and store its chunks."""
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings, dtype=np.float32))
        self._stores[doc_id] = (index, chunks)

    # ── Read ─────────────────────────────────────────────────

    def search(
        self,
        doc_id: str,
        query_embedding: np.ndarray,
        top_k: int | None = None,
    ) -> list[str]:
        """
        Return the top-k most similar chunks for a query embedding.
        """
        if doc_id not in self._stores:
            raise KeyError(f"Document '{doc_id}' not found in vector store")

        settings = get_settings()
        top_k = top_k or settings.TOP_K

        index, chunks = self._stores[doc_id]
        top_k = min(top_k, len(chunks))

        distances, indices = index.search(
            np.array(query_embedding, dtype=np.float32), top_k
        )

        return [chunks[i] for i in indices[0] if i < len(chunks)]

    def get_all_chunks(self, doc_id: str) -> list[str]:
        """Return all stored chunks for a document."""
        if doc_id not in self._stores:
            raise KeyError(f"Document '{doc_id}' not found in vector store")
        return self._stores[doc_id][1]

    # ── Management ───────────────────────────────────────────

    def delete_document(self, doc_id: str) -> bool:
        """Remove a document's index and chunks. Returns True if found."""
        return self._stores.pop(doc_id, None) is not None

    def list_documents(self) -> list[str]:
        """Return IDs of all indexed documents."""
        return list(self._stores.keys())

    def document_chunk_count(self, doc_id: str) -> int:
        """Return the number of chunks stored for a document."""
        if doc_id not in self._stores:
            return 0
        return len(self._stores[doc_id][1])

    @property
    def total_documents(self) -> int:
        return len(self._stores)


# ── Module-level singleton ────────────────────────────────────
vector_store = VectorStore()
