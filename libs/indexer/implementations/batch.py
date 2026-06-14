from __future__ import annotations

from typing import ClassVar

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, IndexedChunk
from libs.embedder.base import Embedder
from libs.embedder.implementations.random import RandomEmbedder
from libs.indexer.base import BaseIndexingStrategy


class BatchIndexer(BaseIndexingStrategy):
    """Indexes chunks in batches using an injected Embedder.

    Processes chunks in configurable batches, calling embed_batch() per batch.
    Returns a list of IndexedChunk pairing each chunk with its embedding.
    The consuming layer is responsible for storing results in a vector store.

    Args:
        batch_size: Number of chunks to embed per batch. Default: 32.
        embedder: Injected Embedder. Default: RandomEmbedder.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    def __init__(
        self,
        batch_size: int = 32,
        embedder: Embedder = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {batch_size}")
        self._batch_size = batch_size
        self._embedder = embedder or RandomEmbedder()

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        if not chunks:
            return []

        results = []

        for i in range(0, len(chunks), self._batch_size):
            batch = chunks[i:i + self._batch_size]
            texts = [chunk.content for chunk in batch]
            embeddings = self._embedder.embed_batch(texts)
            for chunk, embedding in zip(batch, embeddings):
                results.append(IndexedChunk(chunk=chunk, embedding=embedding))

        return results