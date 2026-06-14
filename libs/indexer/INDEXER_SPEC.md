[← LIBS_SPEC](../LIBS_SPEC.md)

# Indexer Module

## Overview

Accepts a list of `DocumentChunk` objects, produces embeddings for each using an
injected `Embedder`, and returns a list of `IndexedChunk` objects pairing each chunk
with its embedding. The consuming layer is responsible for storing the results in a
vector store.

Designed around an ABC and a priority-based registry so that format-specific indexing
strategies can be added incrementally without modifying the core module.

`BatchIndexer` ships as the only concrete implementation and serves as the default
last resort.

---

## Interface Contract

- **Input:** `list[DocumentChunk]` — chunker output
- **Output:** `list[IndexedChunk]` — chunks paired with their embeddings

---

## Embedding

Embedding is injected as a dependency — strategies do not hardcode any embedding logic.
See [EMBEDDER_SPEC.md](embedder/EMBEDDER_SPEC.md) for the full interface contract.

The `Embedder` is injected at strategy construction time by the consuming project.
`RandomEmbedder` is used as the default when no embedder is configured.

---

## Abstract Base: `BaseIndexingStrategy`

All indexing strategy implementations must extend this ABC. No defaults are provided —
every subclass must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this strategy handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(chunks: list[DocumentChunk]) -> bool` | Inspects the chunks to decide suitability. Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `BatchIndexer` declares `1` |
| `index` | `(chunks: list[DocumentChunk]) -> list[IndexedChunk]` | Produces a list of `IndexedChunk` from the given chunks |

---

## Indexer Registry

A `IndexerRegistry` is instantiated by the consuming project and receives its strategy
list directly as a constructor argument.

**At startup**, the registry validates that no two registered strategies share the same
`get_priority()` for the same `FileType` — raises `IndexerPriorityConflictError`, failing
fast before any chunks are indexed.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Registry narrows candidates to strategies whose `supported_mime_types` includes the chunks' `FileType` |
| 2. `can_handle` | Each candidate inspects the chunk list |
| 3. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |

Raises `NoIndexingStrategyFoundError` if no candidate survives steps 1–2.

---

## `BatchIndexer`

The default and only concrete indexing strategy shipped with the module. Handles all
`FileType` values. Processes chunks in configurable batches, calling
`embedder.embed_batch()` per batch.

| Attribute | Value |
|---|---|
| `supported_mime_types` | All `FileType` values including `UNKNOWN` |
| `get_priority()` | `1` |
| `can_handle` | Always `True` |
| Default `batch_size` | `32` |
| Default `Embedder` | `RandomEmbedder` |

### Algorithm

1. Split chunks into batches of `batch_size`
2. For each batch, extract `content` from each chunk
3. Call `embedder.embed_batch(texts)` to produce embeddings
4. Pair each chunk with its embedding into an `IndexedChunk`
5. Return the full list of `IndexedChunk` objects

### Edge Cases

- Empty chunk list returns empty list
- Last batch may be smaller than `batch_size`

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Embedding | Injected via `Embedder` ABC |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── indexer/
    ├── __init__.py
    ├── base.py                           # BaseIndexingStrategy ABC
    ├── registry.py                       # IndexerRegistry, errors
    ├── embedder/
    │   ├── __init__.py
    │   ├── base.py                       # Embedder ABC
    │   └── implementations/
    │       ├── __init__.py
    │       └── random.py                 # RandomEmbedder
    └── implementations/
        ├── __init__.py
        └── batch.py                      # BatchIndexer
tests/
└── test_libs/
    └── indexer/
        ├── test_registry.py
        ├── embedder/
        │   └── implementations/
        │       └── test_random.py
        └── implementations/
            └── test_batch.py
```

---

## Implementation Order

1. `Embedder` ABC + `RandomEmbedder`
2. `BaseIndexingStrategy` ABC
3. `IndexerRegistry` + errors
4. `BatchIndexer`
5. Tests at each stage

---

## Acceptance Criteria

- [ ] `IndexedChunk` dataclass defined in `common/models.py` with: `chunk`, `embedding`
- [ ] `Embedder` ABC defined with: `dimension` property, `embed`, `embed_batch`
- [ ] `RandomEmbedder` returns unit vectors of configurable dimension, defaults to `768`
- [ ] `BaseIndexingStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `index` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `IndexerRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `IndexerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoIndexingStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`
- [ ] `BatchIndexer` declares `supported_mime_types` covering all `FileType` values including `UNKNOWN`
- [ ] `BatchIndexer` `can_handle` always returns `True`
- [ ] `BatchIndexer` `get_priority` always returns `1`
- [ ] `BatchIndexer` default `batch_size` is `32`
- [ ] `BatchIndexer` default `Embedder` is `RandomEmbedder`
- [ ] `BatchIndexer` calls `embed_batch` per batch
- [ ] `BatchIndexer` returns one `IndexedChunk` per input chunk
- [ ] `BatchIndexer` handles empty chunk list — returns empty list
- [ ] `BatchIndexer` handles last batch smaller than `batch_size`
- [ ] Embedder injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoIndexingStrategyFoundError`, batch processing, embedding dimension, empty input, `embed_batch` called per batch