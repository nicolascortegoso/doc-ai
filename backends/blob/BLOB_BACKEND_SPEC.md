[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Blob Backend

## Overview

Provides a `BlobStore` ABC for binary object storage. Each `BlobStore` instance
is scoped to a single collection at construction time. Designed for dependency
injection so that consuming modules remain decoupled from any specific storage
implementation.

`InMemoryBlobStore` ships as the only concrete implementation.

---

## Interface Contract

### `BlobStore` ABC

Defined in `backends/blob/base.py`.

Each instance is scoped to a single collection, mapping naturally to concepts
like buckets (MinIO, S3) or directories (filesystem).

| Method | Signature | Description |
|---|---|---|
| `save` | `(key: str, data: bytes) -> str` | Store data under the given key. Returns the URI. |
| `get` | `(key: str) -> bytes` | Retrieve data by key. Raises `BlobNotFoundError` if not found. |
| `delete` | `(key: str) -> None` | Remove data by key. No-op if key does not exist. |
| `exists` | `(key: str) -> bool` | Returns `True` if the key exists, `False` otherwise. |

### `BlobNotFoundError`

Raised by `get` when the requested key does not exist in the store.

---

## `InMemoryBlobStore`

Defined in `backends/blob/implementations/memory.py`. Stores data in a Python
dict. Accepts a `collection` name at construction time. The URI returned by
`save` is `{collection}/{key}`. Used for testing and local development.
Not thread-safe.

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
└── blob/
    ├── __init__.py
    ├── base.py                       # BlobStore ABC, BlobNotFoundError
    └── implementations/
        ├── __init__.py
        └── memory.py                 # InMemoryBlobStore
tests/
└── test_backends/
    └── blob/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_memory.py
```

---

## Implementation Order

1. `BlobNotFoundError` + `BlobStore` ABC
2. `InMemoryBlobStore`
3. Tests

---

## Acceptance Criteria

- [ ] `BlobNotFoundError` defined in `backends/blob/base.py`
- [ ] `BlobStore` ABC defined with: `save`, `get`, `delete`, `exists`
- [ ] `BlobStore` accepts `collection` at construction time
- [ ] `save` returns a URI string
- [ ] `get` raises `BlobNotFoundError` when key does not exist
- [ ] `delete` is a no-op when key does not exist
- [ ] `exists` returns `True` for existing keys, `False` otherwise
- [ ] `InMemoryBlobStore` accepts `collection` at construction time
- [ ] `InMemoryBlobStore.save` stores data and returns `{collection}/{key}` as URI
- [ ] `InMemoryBlobStore.get` raises `BlobNotFoundError` for missing keys
- [ ] `InMemoryBlobStore.delete` removes data without raising for missing keys
- [ ] `InMemoryBlobStore.exists` returns correct boolean
- [ ] Unit tests cover: save and retrieve, get raises for missing key, delete removes data, delete is no-op for missing key, exists returns correct boolean, URI format