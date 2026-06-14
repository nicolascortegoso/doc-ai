[← PIPELINES_SPEC](../PIPELINES_SPEC.md)

# Ingestion Pipeline

## Overview

Orchestrates document ingestion from raw bytes to fully indexed state. Each stage
reads its input from the record and blob stores, runs the corresponding domain
logic, writes its output back, and updates the ingestion status. On failure, the
status is set to `FAILED`.

Designed as an ABC so that concrete implementations (synchronous, Celery, etc.)
can override individual stages or the full `run()` method without modifying the
core contract.

---

## Interface Contract

### `IngestionPipeline` ABC

Defined in `pipelines/ingestion/base.py`.

| Method | Signature | Description |
|---|---|---|
| `profile` | `(document_id: UUID) -> None` | Run profiler stage |
| `parse` | `(document_id: UUID) -> None` | Run parser stage |
| `chunk` | `(document_id: UUID) -> None` | Run chunker stage |
| `merge` | `(document_id: UUID) -> None` | Run merger stage |
| `index` | `(document_id: UUID) -> None` | Run indexer stage, store chunks in vector store, store tree in graph store |
| `run` | `(document_id: UUID) -> None` | Run all stages in order |

---

## Stage Contract

Each stage method follows the same contract:

1. Read `DocumentRecord` from `RecordStore`
2. Update status to in-progress (e.g. `PROFILING`)
3. Read input from `BlobStore` if needed
4. Run the corresponding registry
5. Serialize output and write to `BlobStore`
6. Update `DocumentRecord` URI field
7. Update status to complete (e.g. `PROFILED`)
8. On any exception — update status to `FAILED` and re-raise

---

## Stage I/O

| Stage | Reads from | Writes to | Status transition |
|---|---|---|---|
| `profile` | Raw bytes from `BlobStore` | `DocumentProfile` to `BlobStore` | `PROFILING` → `PROFILED` |
| `parse` | Raw bytes + `DocumentProfile` from `BlobStore` | `ParsedDocument` to `BlobStore` | `PARSING` → `PARSED` |
| `chunk` | `ParsedDocument` from `BlobStore` | `list[DocumentChunk]` to `BlobStore` | `CHUNKING` → `CHUNKED` |
| `merge` | `list[DocumentChunk]` from `BlobStore` | `DocumentTree` to `BlobStore` | `MERGING` → `MERGED` |
| `index` | `list[DocumentChunk]` from `BlobStore` | Chunks to `VectorStore`, tree to `GraphStore` | `EMBEDDING` → `INDEXED` |

---

## Injected Dependencies

All dependencies are injected at construction time.

| Dependency | Type | Description |
|---|---|---|
| `record_store` | `RecordStore` | Track ingestion status |
| `blob_store` | `BlobStore` | Read/write pipeline outputs |
| `profiler_registry` | `ProfilerRegistry` | Profile stage |
| `parser_registry` | `ParserRegistry` | Parse stage |
| `chunker_registry` | `ChunkerRegistry` | Chunk stage |
| `merger_registry` | `MergerRegistry` | Merge stage |
| `indexer_registry` | `IndexerRegistry` | Index stage |
| `vector_store` | `VectorStore` | Store indexed chunks |
| `graph_store` | `GraphStore` | Store document tree |

---

## Serialisation

Pipeline outputs (`DocumentProfile`, `ParsedDocument`, `list[DocumentChunk]`,
`DocumentTree`) are serialised to JSON before writing to `BlobStore` and
deserialised when reading back. Serialisation logic is owned by the pipeline,
not by the domain models or the stores.

---

## `run()` Default Implementation

The default `run()` implementation calls each stage method in order:

```python
def run(self, document_id: UUID) -> None:
    self.profile(document_id)
    self.parse(document_id)
    self.chunk(document_id)
    self.merge(document_id)
    self.index(document_id)
```

Concrete implementations (e.g. Celery) may override `run()` to dispatch each
stage as a separate task.

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Serialisation | JSON via `dataclasses` + custom serialisers |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
pipelines/
└── ingestion/
    ├── __init__.py
    ├── base.py                       # IngestionPipeline ABC
    └── serializers.py                # Pipeline output serialisers
tests/
└── test_pipelines/
    └── ingestion/
        ├── __init__.py
        └── test_base.py
```

---

## Implementation Order

1. Serialisers for `DocumentProfile`, `ParsedDocument`, `list[DocumentChunk]`, `DocumentTree`
2. `IngestionPipeline` ABC with default `run()` implementation
3. Tests using `InMemory*` backends

---

## Acceptance Criteria

- [ ] `IngestionPipeline` ABC defined with: `profile`, `parse`, `chunk`, `merge`, `index`, `run`
- [ ] All dependencies injected at construction time
- [ ] Each stage updates status to in-progress before running
- [ ] Each stage updates status to complete after running
- [ ] Each stage updates status to `FAILED` on exception and re-raises
- [ ] Each stage reads and writes to `BlobStore` via URI stored in `DocumentRecord`
- [ ] `run()` default implementation calls all stages in order
- [ ] Serialisers handle `DocumentProfile`, `ParsedDocument`, `list[DocumentChunk]`, `DocumentTree`
- [ ] Serialisers round-trip without data loss
- [ ] Unit tests cover: each stage status transition, `FAILED` on exception, `run()` calls all stages, serialiser round-trips