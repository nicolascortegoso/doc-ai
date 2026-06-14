[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Graph Backend

## Overview

Provides a `GraphStore` ABC for storing and retrieving `DocumentTree` objects.
Each `DocumentTree` is stored as a graph structure — nodes and edges — enabling
tree-level operations and node-level traversal.

Designed for dependency injection so that consuming modules remain decoupled from
any specific graph store implementation.

`InMemoryGraphStore` ships as the only concrete implementation.

---

## Data Model Updates

The following fields are added to existing models in `common/models.py`:

### `TreeNode`

| New Field | Type | Description |
|---|---|---|
| `id` | `UUID` | Unique identifier, defaults to `uuid4()` |

### `DocumentTree`

| New Field | Type | Description |
|---|---|---|
| `document_id` | `UUID | None` | Reference to the originating document. Defaults to `None`. Set by the consuming layer. |

---

## Interface Contract

### `GraphStore` ABC

Defined in `backends/graph/base.py`.

| Method | Signature | Description |
|---|---|---|
| `save` | `(tree: DocumentTree) -> None` | Persist the full tree |
| `get` | `(document_id: UUID) -> DocumentTree | None` | Retrieve a tree by document ID. Returns `None` if not found |
| `delete` | `(document_id: UUID) -> None` | Remove a tree. No-op if not found |
| `exists` | `(document_id: UUID) -> bool` | Returns `True` if a tree exists for the given document ID |
| `get_node` | `(node_id: UUID) -> TreeNode | None` | Retrieve a node by ID. Returns `None` if not found |
| `get_children` | `(node_id: UUID) -> list[TreeNode]` | Retrieve direct children of a node. Returns empty list if node not found |
| `get_root` | `(document_id: UUID) -> TreeNode | None` | Retrieve the root node of a tree. Returns `None` if not found |

---

## `InMemoryGraphStore`

Defined in `backends/graph/implementations/memory.py`. Stores trees in a Python
dict keyed by `document_id`. Traversal methods operate directly on the in-memory
tree structure. Not thread-safe. Suitable for testing and local development only.

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
└── graph/
    ├── __init__.py
    ├── base.py                       # GraphStore ABC
    └── implementations/
        ├── __init__.py
        └── memory.py                 # InMemoryGraphStore
tests/
└── test_backends/
    └── graph/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_memory.py
```

---

## Implementation Order

1. Update `TreeNode` in `common/models.py` — add `id: UUID`
2. Update `DocumentTree` in `common/models.py` — add `document_id: UUID | None`
3. `GraphStore` ABC
4. `InMemoryGraphStore`
5. Tests

---

## Acceptance Criteria

- [ ] `TreeNode` updated with `id: UUID` defaulting to `uuid4()`
- [ ] `DocumentTree` updated with `document_id: UUID | None` defaulting to `None`
- [ ] `GraphStore` ABC defined with: `save`, `get`, `delete`, `exists`, `get_node`, `get_children`, `get_root`
- [ ] `get` returns `None` when document ID not found
- [ ] `delete` is a no-op when document ID not found
- [ ] `get_node` returns `None` when node ID not found
- [ ] `get_children` returns empty list when node ID not found
- [ ] `get_root` returns `None` when document ID not found
- [ ] `InMemoryGraphStore.save` persists the full tree
- [ ] `InMemoryGraphStore.get` returns the correct tree
- [ ] `InMemoryGraphStore.delete` removes the tree
- [ ] `InMemoryGraphStore.exists` returns correct boolean
- [ ] `InMemoryGraphStore.get_node` returns correct node
- [ ] `InMemoryGraphStore.get_children` returns direct children only
- [ ] `InMemoryGraphStore.get_root` returns the root node
- [ ] Unit tests cover: save and get, delete removes tree, exists returns correct boolean, get_node returns correct node, get_children returns direct children, get_root returns root, None/empty returns for missing items