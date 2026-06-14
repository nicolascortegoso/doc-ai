from __future__ import annotations

from uuid import uuid4

import pytest

from libs.common.enums import FileType
from libs.common.models import DocumentChunk, SourceReference
from backends.vector.models import SearchResult
from backends.vector.implementations.memory import InMemoryVectorStore


def _make_chunk(content: str = "chunk content", mime_type: FileType = FileType.PDF) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=mime_type,
        strategy="PlainPdfExtractionStrategy",
    )


def _unit_vector(dims: int, index: int) -> list[float]:
    v = [0.0] * dims
    v[index] = 1.0
    return v


@pytest.fixture
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


class TestInMemoryVectorStoreUpsert:
    def test_upsert_stores_chunk(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        assert store.exists(chunk.id)

    def test_upsert_overwrites_existing_chunk(self, store):
        chunk = _make_chunk(content="original")
        store.upsert(chunk, [1.0, 0.0])
        chunk.content = "updated"
        store.upsert(chunk, [0.0, 1.0])
        results = store.search([0.0, 1.0], top_k=1)
        assert results[0].chunk.content == "updated"


class TestInMemoryVectorStoreSearch:
    def test_search_empty_store_returns_empty_list(self, store):
        assert store.search([1.0, 0.0], top_k=5) == []

    def test_search_returns_most_similar_chunk_first(self, store):
        chunk_a = _make_chunk(content="chunk A")
        chunk_b = _make_chunk(content="chunk B")
        store.upsert(chunk_a, _unit_vector(3, 0))
        store.upsert(chunk_b, _unit_vector(3, 1))
        results = store.search(_unit_vector(3, 0), top_k=2)
        assert results[0].chunk.content == "chunk A"

    def test_search_respects_top_k(self, store):
        for i in range(5):
            chunk = _make_chunk(content=f"chunk {i}")
            store.upsert(chunk, _unit_vector(5, i))
        results = store.search(_unit_vector(5, 0), top_k=3)
        assert len(results) <= 3

    def test_search_results_sorted_by_score_descending(self, store):
        chunk_a = _make_chunk(content="chunk A")
        chunk_b = _make_chunk(content="chunk B")
        chunk_c = _make_chunk(content="chunk C")
        store.upsert(chunk_a, [1.0, 0.0, 0.0])
        store.upsert(chunk_b, [0.8, 0.2, 0.0])
        store.upsert(chunk_c, [0.0, 0.0, 1.0])
        results = store.search([1.0, 0.0, 0.0], top_k=3)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_score_is_float(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        results = store.search([1.0, 0.0], top_k=1)
        assert isinstance(results[0].score, float)

    def test_search_identical_vector_returns_score_of_1(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        results = store.search([1.0, 0.0], top_k=1)
        assert abs(results[0].score - 1.0) < 1e-6

    def test_search_ignores_filters(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        results = store.search([1.0, 0.0], top_k=1, filters={"mime_type": "application/pdf"})
        assert len(results) == 1


class TestInMemoryVectorStoreDelete:
    def test_delete_removes_chunk(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        store.delete(chunk.id)
        assert not store.exists(chunk.id)

    def test_delete_is_noop_for_missing_chunk(self, store):
        store.delete(uuid4())

    def test_delete_does_not_affect_other_chunks(self, store):
        chunk_a = _make_chunk(content="A")
        chunk_b = _make_chunk(content="B")
        store.upsert(chunk_a, [1.0, 0.0])
        store.upsert(chunk_b, [0.0, 1.0])
        store.delete(chunk_a.id)
        assert store.exists(chunk_b.id)


class TestInMemoryVectorStoreExists:
    def test_exists_returns_true_for_stored_chunk(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        assert store.exists(chunk.id) is True

    def test_exists_returns_false_for_missing_chunk(self, store):
        assert store.exists(uuid4()) is False

    def test_exists_returns_false_after_delete(self, store):
        chunk = _make_chunk()
        store.upsert(chunk, [1.0, 0.0])
        store.delete(chunk.id)
        assert store.exists(chunk.id) is False


class TestInMemoryVectorStoreDocumentId:
    def test_document_id_preserved_through_upsert_and_search(self, store):
        doc_id = uuid4()
        chunk = _make_chunk()
        chunk.document_id = doc_id
        store.upsert(chunk, [1.0, 0.0])
        results = store.search([1.0, 0.0], top_k=1)
        assert results[0].chunk.document_id == doc_id