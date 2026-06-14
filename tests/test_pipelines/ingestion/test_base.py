from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backends.blob.implementations.memory import InMemoryBlobStore
from backends.graph.implementations.memory import InMemoryGraphStore
from backends.record.enums import IngestionStatus
from backends.record.implementations.memory import InMemoryRecordStore
from backends.record.models import DocumentRecord
from backends.vector.implementations.memory import InMemoryVectorStore
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
from libs.indexer.implementations.batch import BatchIndexer
from libs.indexer.registry import IndexerRegistry
from libs.merger.implementations.bottom_up import BottomUpMergingStrategy
from libs.merger.registry import MergerRegistry
from libs.profiler.detector.implementations.default import DefaultDetector
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.pdf import PdfProfiler
from libs.profiler.registry import ProfilerRegistry
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.plain_pdf import PlainPdfExtractionStrategy
from libs.parser.registry import ParserRegistry
from pipelines.ingestion.base import IngestionPipeline


class SynchronousIngestionPipeline(IngestionPipeline):
    """Concrete synchronous implementation for testing."""
    pass


@pytest.fixture
def document_id():
    return uuid4()


@pytest.fixture
def record_store():
    return InMemoryRecordStore()


@pytest.fixture
def blob_store():
    return InMemoryBlobStore(collection="test")


@pytest.fixture
def pipeline(record_store, blob_store):
    detector = DefaultDetector()
    return SynchronousIngestionPipeline(
        record_store=record_store,
        blob_store=blob_store,
        profiler_registry=ProfilerRegistry(
            profilers=[PdfProfiler(detector=detector), DefaultProfiler()],
            detector=detector,
        ),
        parser_registry=ParserRegistry(
            strategies=[PlainPdfExtractionStrategy(), DefaultPageExtractionStrategy()],
        ),
        chunker_registry=ChunkerRegistry(
            strategies=[SlidingWindowChunkingStrategy()],
        ),
        merger_registry=MergerRegistry(
            strategies=[BottomUpMergingStrategy()],
        ),
        indexer_registry=IndexerRegistry(
            strategies=[BatchIndexer()],
        ),
        vector_store=InMemoryVectorStore(),
        graph_store=InMemoryGraphStore(),
    )


def _make_record(document_id) -> DocumentRecord:
    return DocumentRecord(
        id=document_id,
        status=IngestionStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _save_raw(blob_store, document_id, content: bytes = b"raw file bytes") -> None:
    blob_store.save(f"{document_id}/raw", content)


class TestIngestionPipelineProfile:
    def test_profile_updates_status_to_profiled(self, pipeline, record_store, blob_store, document_id):
        record_store.save(_make_record(document_id))
        _save_raw(blob_store, document_id)
        pipeline.profile(document_id)
        assert record_store.get(document_id).status == IngestionStatus.PROFILED

    def test_profile_writes_profile_uri(self, pipeline, record_store, blob_store, document_id):
        record_store.save(_make_record(document_id))
        _save_raw(blob_store, document_id)
        pipeline.profile(document_id)
        assert record_store.get(document_id).profile_uri is not None

    def test_profile_sets_failed_on_exception(self, pipeline, record_store, document_id):
        record_store.save(_make_record(document_id))
        with pytest.raises(Exception):
            pipeline.profile(document_id)
        assert record_store.get(document_id).status == IngestionStatus.FAILED


class TestIngestionPipelineRun:
    def test_run_calls_all_stages(self, pipeline, record_store, blob_store, document_id):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "hello world " * 100)
        raw_bytes = doc.tobytes()
        doc.close()

        record_store.save(_make_record(document_id))
        _save_raw(blob_store, document_id, raw_bytes)
        pipeline.run(document_id)
        assert record_store.get(document_id).status == IngestionStatus.INDEXED