# pipelines/ — Orchestration Layer

[← README](../README.md)

## Principles

`pipelines/` contains orchestration abstractions. Every module defines an ABC
for a specific pipeline concern. Concrete implementations (Celery, synchronous,
etc.) live in `infrastructure/`.

## Rules

- No imports from `infrastructure/` or any framework
- May import from `libs/` and `backends/`
- Defines stage contracts, not execution strategies
- Every pipeline is fully resumable via `IngestionStatus`

## Pattern

```
pipelines/<pipeline>/
    base.py              # Pipeline ABC
    models.py            # Pipeline-specific models (where needed)
```

## Dependency Direction

```
pipelines/ → libs/ + backends/
```

## `IngestionPipeline`

Defined in `pipelines/ingestion/base.py`.

Orchestrates document ingestion from raw bytes to fully indexed state.
Defines individual stage methods and a `run()` method that calls them
in order.

| Method | Description |
|---|---|
| `profile(document_id: UUID) -> None` | Run profiler stage |
| `parse(document_id: UUID) -> None` | Run parser stage |
| `chunk(document_id: UUID) -> None` | Run chunker stage |
| `merge(document_id: UUID) -> None` | Run merger stage |
| `index(document_id: UUID) -> None` | Run indexer stage |
| `run(document_id: UUID) -> None` | Run all stages in order |

Each stage method:
- Reads its input from `RecordStore` / `BlobStore`
- Runs the corresponding `libs/` pipeline stage
- Writes its output to `BlobStore` / `VectorStore` / `GraphStore`
- Updates `IngestionStatus` in `RecordStore`

## Pipeline Specs

| Pipeline | Spec |
|---|---|
| `ingestion/` | _(coming soon)_ |
| `inference/` | _(coming soon)_ |