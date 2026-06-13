from abc import ABC, abstractmethod
from uuid import UUID

from libs.common.models import DocumentChunk
from backends.vector.models import SearchResult


class VectorStore(ABC):
    """Abstract base for vector store implementations.

    Stores document chunk embeddings and supports similarity search.
    """

    @abstractmethod
    def upsert(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        """Store or update a chunk with its embedding."""

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        """Find the most similar chunks to the query vector.

        Returns up to top_k results sorted by score descending.
        Filters are implementation-specific — pass None to disable filtering.
        """

    @abstractmethod
    def delete(self, chunk_id: UUID) -> None:
        """Remove a chunk by ID. No-op if not found."""

    @abstractmethod
    def exists(self, chunk_id: UUID) -> bool:
        """Returns True if the chunk exists, False otherwise."""