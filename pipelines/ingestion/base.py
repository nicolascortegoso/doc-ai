from __future__ import annotations

import json
from abc import ABC
from uuid import UUID

from common.models import (
    DocumentChunk,
    DocumentProfile,
    DocumentTree,
    ParsedDocument,
)
from backends.blob.base import BlobStore
from backends.graph.base import GraphStore
from backends.record.base import RecordStore
from backends.record.enums import IngestionStatus
from backends.vector.base import VectorStore
from libs.chunker.registry import ChunkerRegistry
from libs.indexer.registry import IndexerRegistry
from libs.merger.registry import MergerRegistry
from libs.parser.registry import ParserRegistry
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.serializers import (
    DocumentChunkSerializer,
    DocumentProfileSerializer,
    DocumentTreeSerializer,
    ParsedDocumentSerializer,
)


class IngestionPipeline(ABC):
    """Abstract base for ingestion pipeline implementations.

    Orchestrates document ingestion from raw bytes to fully indexed state.
    Each stage reads its input from the record and blob stores, runs the
    corresponding domain logic, writes its output back, and updates the
    ingestion status. On failure, the status is set to FAILED.

    Concrete implementations (synchronous, Celery, etc.) may override
    individual stage methods or run() without modifying this contract.
    """

    def __init__(
        self,
        record_store: RecordStore,
        blob_store: BlobStore,
        profiler_registry: ProfilerRegistry,
        parser_registry: ParserRegistry,
        chunker_registry: ChunkerRegistry,
        merger_registry: MergerRegistry,
        indexer_registry: IndexerRegistry,
        vector_store: VectorStore,
        graph_store: GraphStore,
    ) -> None:
        self._record_store = record_store
        self._blob_store = blob_store
        self._profiler_registry = profiler_registry
        self._parser_registry = parser_registry
        self._chunker_registry = chunker_registry
        self._merger_registry = merger_registry
        self._indexer_registry = indexer_registry
        self._vector_store = vector_store
        self._graph_store = graph_store
        self._profile_serializer = DocumentProfileSerializer()
        self._parsed_document_serializer = ParsedDocumentSerializer()
        self._chunk_serializer = DocumentChunkSerializer()
        self._tree_serializer = DocumentTreeSerializer()

    def profile(self, document_id: UUID) -> None:
        record = self._record_store.get(document_id)
        record.status = IngestionStatus.PROFILING
        self._record_store.update(record)
        try:
            raw_bytes = self._blob_store.get(f"{document_id}/raw")
            profile = self._profiler_registry.profile(raw_bytes)
            uri = self._blob_store.save(
                f"{document_id}/profile.json",
                json.dumps(self._profile_serializer.to_dict(profile)).encode(),
            )
            record.profile_uri = uri
            record.status = IngestionStatus.PROFILED
            self._record_store.update(record)
        except Exception:
            record.status = IngestionStatus.FAILED
            self._record_store.update(record)
            raise

    def parse(self, document_id: UUID) -> None:
        record = self._record_store.get(document_id)
        record.status = IngestionStatus.PARSING
        self._record_store.update(record)
        try:
            raw_bytes = self._blob_store.get(f"{document_id}/raw")
            profile_bytes = self._blob_store.get(f"{document_id}/profile.json")
            profile = self._profile_serializer.from_dict(json.loads(profile_bytes))
            parsed_document = self._parser_registry.parse(raw_bytes, profile)
            uri = self._blob_store.save(
                f"{document_id}/parsed.json",
                json.dumps(self._parsed_document_serializer.to_dict(parsed_document)).encode(),
            )
            record.parsed_document_uri = uri
            record.status = IngestionStatus.PARSED
            self._record_store.update(record)
        except Exception:
            record.status = IngestionStatus.FAILED
            self._record_store.update(record)
            raise

    def chunk(self, document_id: UUID) -> None:
        record = self._record_store.get(document_id)
        record.status = IngestionStatus.CHUNKING
        self._record_store.update(record)
        try:
            parsed_bytes = self._blob_store.get(f"{document_id}/parsed.json")
            parsed_document = self._parsed_document_serializer.from_dict(json.loads(parsed_bytes))
            chunks = self._chunker_registry.chunk(parsed_document)
            for chunk in chunks:
                chunk.document_id = document_id
            uri = self._blob_store.save(
                f"{document_id}/chunks.json",
                json.dumps(self._chunk_serializer.list_to_dict(chunks)).encode(),
            )
            record.status = IngestionStatus.CHUNKED
            self._record_store.update(record)
        except Exception:
            record.status = IngestionStatus.FAILED
            self._record_store.update(record)
            raise

    def merge(self, document_id: UUID) -> None:
        record = self._record_store.get(document_id)
        record.status = IngestionStatus.MERGING
        self._record_store.update(record)
        try:
            chunks_bytes = self._blob_store.get(f"{document_id}/chunks.json")
            chunks = self._chunk_serializer.list_from_dict(json.loads(chunks_bytes))
            tree = self._merger_registry.merge(chunks)
            tree.document_id = document_id
            uri = self._blob_store.save(
                f"{document_id}/tree.json",
                json.dumps(self._tree_serializer.to_dict(tree)).encode(),
            )
            record.tree_uri = uri
            record.status = IngestionStatus.MERGED
            self._record_store.update(record)
        except Exception:
            record.status = IngestionStatus.FAILED
            self._record_store.update(record)
            raise

    def index(self, document_id: UUID) -> None:
        record = self._record_store.get(document_id)
        record.status = IngestionStatus.EMBEDDING
        self._record_store.update(record)
        try:
            chunks_bytes = self._blob_store.get(f"{document_id}/chunks.json")
            chunks = self._chunk_serializer.list_from_dict(json.loads(chunks_bytes))
            tree_bytes = self._blob_store.get(f"{document_id}/tree.json")
            tree = self._tree_serializer.from_dict(json.loads(tree_bytes))
            indexed_chunks = self._indexer_registry.index(chunks)
            for indexed_chunk in indexed_chunks:
                self._vector_store.upsert(indexed_chunk.chunk, indexed_chunk.embedding)
            self._graph_store.save(tree)
            record.status = IngestionStatus.INDEXED
            self._record_store.update(record)
        except Exception:
            record.status = IngestionStatus.FAILED
            self._record_store.update(record)
            raise

    def run(self, document_id: UUID) -> None:
        """Run all stages in order.

        Concrete implementations may override this to dispatch stages
        as separate tasks (e.g. Celery).
        """
        self.profile(document_id)
        self.parse(document_id)
        self.chunk(document_id)
        self.merge(document_id)
        self.index(document_id)