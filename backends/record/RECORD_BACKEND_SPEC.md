# Record Backend

## Overview

Provides a `RecordStore` ABC for tracking document ingestion state. Stores
lightweight `DocumentRecord` objects — status, timestamps, and URIs pointing to
pipeline outputs in external storage. Designed for dependency injection so that
consuming modules remain decoupled from any specific storage implementation.

`InMemoryRecordStore` ships as the only concrete implementation.

---

## Data Models

### `IngestionStatus` Enum

Defined in `backends/record/enums.py`.

Represents the current state of a document in the ingestion pipeline.

### `DocumentRecord` Dataclass

Defined in `backends/record/models.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `UUID` | Internal unique identifier |
| `external_id` | `str | None` | Identifier in an external system |
| `status` | `IngestionStatus` | Current ingestion state |
| `created_at` | `datetime` | Record creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |
| `profile_uri` | `str | None` | URI to stored `DocumentProfile` |
| `parsed_document_uri` | `str | None` | URI to stored `ParsedDocument` |
| `tree_uri` | `str | None` | URI to stored `DocumentTree` |

---

## Serialisation

### `DocumentRecordSerializer`

Defined in `backends/record/serializer.py`. Converts `DocumentRecord`
to and from a portable `dict` representation. Used by all store implementations
to avoid duplicating serialisation logic.

| Method | Signature | Description |
|---|---|---|
| `to_dict` | `(record: DocumentRecord) -> dict` | Serialise to dict |
| `from_dict` | `(data: dict) -> DocumentRecord` | Deserialise from dict |

---

## Interface Contract

### `RecordStore` ABC

Defined in `backends/record/base.py`.

| Method | Signature | Description |
|---|---|---|
| `save` | `(record: DocumentRecord) -> None` | Persist a new record |
| `get` | `(id: UUID) -> DocumentRecord | None` | Retrieve by internal ID |
| `update` | `(record: DocumentRecord) -> None` | Update an existing record |
| `delete` | `(id: UUID) -> None` | Remove a record |
| `find_by_external_id` | `(external_id: str) -> DocumentRecord | None` | Retrieve by external ID |
| `find_by_status` | `(status: IngestionStatus) -> list[DocumentRecord]` | Retrieve all records with given status |

---

## `InMemoryRecordStore`

Defined in `backends/record/implementations/memory.py`. Stores records
in a Python dict keyed by `id`. Used for testing and local development.
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
└── record/
    ├── __init__.py
    ├── enums.py                      # IngestionStatus
    ├── models.py                     # DocumentRecord
    ├── base.py                       # RecordStore ABC
    ├── serializer.py                 # DocumentRecordSerializer
    └── implementations/
        ├── __init__.py
        └── memory.py                 # InMemoryRecordStore
tests/
└── backends/
    └── record/
        ├── __init__.py
        ├── test_models.py
        ├── test_serializer.py
        └── implementations/
            ├── __init__.py
            └── test_memory.py
```

---

## Implementation Order

1. `IngestionStatus` enum
2. `DocumentRecord` dataclass
3. `DocumentRecordSerializer`
4. `RecordStore` ABC
5. `InMemoryRecordStore`
6. Tests at each stage

---

## Acceptance Criteria

- [ ] `IngestionStatus` enum defined with all pipeline states
- [ ] `DocumentRecord` dataclass defined with: `id`, `external_id`, `status`, `created_at`, `updated_at`, `profile_uri`, `parsed_document_uri`, `tree_uri`
- [ ] `DocumentRecordSerializer.to_dict` serialises all fields to a portable dict
- [ ] `DocumentRecordSerializer.from_dict` deserialises all fields correctly
- [ ] `DocumentRecordSerializer` round-trips without data loss
- [ ] `RecordStore` ABC defined with: `save`, `get`, `update`, `delete`, `find_by_external_id`, `find_by_status`
- [ ] `InMemoryRecordStore.save` persists a new record
- [ ] `InMemoryRecordStore.get` returns the record or `None`
- [ ] `InMemoryRecordStore.update` updates an existing record
- [ ] `InMemoryRecordStore.delete` removes the record
- [ ] `InMemoryRecordStore.find_by_external_id` returns matching record or `None`
- [ ] `InMemoryRecordStore.find_by_status` returns all matching records
- [ ] Unit tests cover: serialisation round-trip, all store operations, `None` returns for missing records, `find_by_status` with multiple records
