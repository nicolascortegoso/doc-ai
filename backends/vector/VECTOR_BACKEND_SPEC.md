[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Vector Backend

## Overview

Provides a `VectorStore` ABC for storing and retrieving document chunk embeddings.
Designed for dependency injection so that consuming modules remain decoupled from
any specific vector store implementation.

`InMemoryVectorStore` ships as the only concrete implementation, using brute-force
cosine similarity search.

---

## Data Models

### `SearchResult` Dataclass

Defined in `backends/vector/models.py`.

| Field | Type | Description |
|---|---|---|
| `chunk` | `DocumentChunk` | The matching chunk |
| `score` | `float` | Similarity score — higher is more similar |

---

## Interface Contract

### `VectorStore` ABC

Defined in `backends/vector/base.py`.

| Method | Signature | Description |
|---|---|---|
| `upsert` | `(chunk: DocumentChunk, embedding: list[float]) -> None` | Store or update a chunk with its embedding |
| `search` | `(query_vector: list[float], top_k: int, filters: dict | None = None) -> list[SearchResult]` | Find the most similar chunks to the query vector |
| `delete` | `(chunk_id: UUID) -> None` | Remove a chunk by ID. No-op if not found |
| `exists` | `(chunk_id: UUID) -> bool` | Returns `True` if the chunk exists, `False` otherwise |

### Filtering

The `filters` parameter in `search` is a plain `dict`. Each implementation
interprets it according to its own capabilities. Passing `None` disables filtering.

### Similarity

The similarity metric is determined by the implementation — the ABC makes no
assumptions about the metric used.

---

## `InMemoryVectorStore`

Defined in `backends/vector/implementations/memory.py`. Stores chunks and
embeddings in Python dicts. Uses brute-force cosine similarity for search.
Not thread-safe. Suitable for testing and local development only.
Filters are ignored — no filtering is performed in this implementation.

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
backends/
└── vector/
    ├── __init__.py
    ├── base.py                       # VectorStore ABC
    ├── models.py                     # SearchResult
    └── implementations/
        ├── __init__.py
        └── memory.py                 # InMemoryVectorStore
tests/
└── test_backends/
    └── vector/
        ├── __init__.py
        ├── test_models.py
        └── implementations/
            ├── __init__.py
            └── test_memory.py
```

---

## Implementation Order

1. `SearchResult` dataclass
2. `VectorStore` ABC
3. `InMemoryVectorStore`
4. Tests

---

## Acceptance Criteria

- [ ] `SearchResult` dataclass defined in `backends/vector/models.py` with: `chunk`, `score`
- [ ] `VectorStore` ABC defined with: `upsert`, `search`, `delete`, `exists`
- [ ] `search` accepts optional `filters: dict | None` parameter
- [ ] `delete` is a no-op when chunk does not exist
- [ ] `InMemoryVectorStore.upsert` stores chunk and embedding
- [ ] `InMemoryVectorStore.search` returns results sorted by score descending
- [ ] `InMemoryVectorStore.search` respects `top_k` limit
- [ ] `InMemoryVectorStore.search` uses cosine similarity
- [ ] `InMemoryVectorStore.search` ignores `filters`
- [ ] `InMemoryVectorStore.delete` removes chunk and embedding
- [ ] `InMemoryVectorStore.exists` returns correct boolean
- [ ] `document_id` preserved through upsert and search
- [ ] Unit tests cover: upsert and search, top_k limit, score ordering, delete removes chunk, exists returns correct boolean, search on empty store returns empty list, document_id preserved