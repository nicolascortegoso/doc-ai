[← README](../README.md)

# backends/ — Storage Abstraction Layer

## Principles

`backends/` contains storage abstractions. Every module defines an ABC for a
specific storage paradigm and ships an in-memory implementation for testing
and local development. Concrete production implementations live in the
infrastructure layer.

## Rules

- No imports from `pipelines/`
- May import domain models from `common/` — they are passed in by the consuming layer
- `libs/` modules NEVER import from `backends/`
- Every module ships an `InMemory*` implementation — not thread-safe, for testing only
- Concrete production implementations belong in the infrastructure layer

## Pattern

Every module follows the same structure:

```
backends/<paradigm>/
    base.py              # ABC
    models.py            # Backend-specific models (where needed)
    implementations/
        memory.py        # InMemory implementation
```

## Storage Paradigms

| Paradigm | ABC | Spec |
|---|---|---|
| `record/` | `RecordStore` | [RECORD_BACKEND_SPEC.md](record/RECORD_BACKEND_SPEC.md) |
| `blob/` | `BlobStore` | [BLOB_BACKEND_SPEC.md](blob/BLOB_BACKEND_SPEC.md) |
| `vector/` | `VectorStore` | [VECTOR_BACKEND_SPEC.md](vector/VECTOR_BACKEND_SPEC.md) |
| `graph/` | `GraphStore` | [GRAPH_BACKEND_SPEC.md](graph/GRAPH_BACKEND_SPEC.md) |