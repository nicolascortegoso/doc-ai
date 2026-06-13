from __future__ import annotations

import math
from uuid import UUID

from libs.common.models import DocumentChunk
from backends.vector.base import VectorStore
from backends.vector.models import SearchResult


class InMemoryVectorStore(VectorStore):
    """In-memory vector store using brute-force cosine similarity search.

    Suitable for testing and local development only. Not thread-safe.
    Filters are ignored — no filtering is performed in this implementation.
    """

    def __init__(self) -> None:
        self._chunks: dict[str, DocumentChunk] = {}
        self._embeddings: dict[str, list[float]] = {}

    def upsert(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        key = str(chunk.id)
        self._chunks[key] = chunk
        self._embeddings[key] = embedding

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        if not self._chunks:
            return []

        scores = [
            SearchResult(
                chunk=self._chunks[key],
                score=self._cosine_similarity(query_vector, self._embeddings[key]),
            )
            for key in self._chunks
        ]

        scores.sort(key=lambda r: r.score, reverse=True)
        return scores[:top_k]

    def delete(self, chunk_id: UUID) -> None:
        key = str(chunk_id)
        self._chunks.pop(key, None)
        self._embeddings.pop(key, None)

    def exists(self, chunk_id: UUID) -> bool:
        return str(chunk_id) in self._chunks

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)