# Merger Module

## Overview

Accepts a list of `DocumentChunk` objects and produces a `DocumentTree` by iteratively
merging chunks into progressively more abstract representations until a single root node
describes the entire document. Designed around an ABC and a priority-based registry so
that format-specific merging strategies can be added incrementally without modifying the
core module.

`BottomUpMergingStrategy` ships as the only concrete implementation and serves as the
default last resort.

---

## Interface Contract

- **Input:** `list[DocumentChunk]` — chunker output
- **Output:** `DocumentTree` — hierarchical document representation

---

## Data Models

Defined in `libs/common/models.py`.

### `TreeNode` Dataclass

A node in the `DocumentTree`.

| Field | Type | Description |
|---|---|---|
| `content` | `str` | Text content of this node — extracted at leaf level, reduced at internal levels |
| `level` | `int` | 0 = leaf, 1 = first merge level, 2 = second merge level, etc. |
| `children` | `list[TreeNode]` | Child nodes. Empty for leaf nodes |
| `chunk` | `DocumentChunk | None` | Originating chunk. Populated only at leaf nodes |

#### `source_reference` property

Computed dynamically — never stored:
- Leaf node: returns `self.chunk.source_reference`
- Internal node: spans `page_start` of leftmost leaf to `page_end` of rightmost leaf

### `DocumentTree` Dataclass

Top-level output of the merger.

| Field | Type | Description |
|---|---|---|
| `root` | `TreeNode` | Root node of the tree |
| `mime_type` | `FileType` | MIME type from the originating `DocumentChunk` list |

---

## Reduction

Reduction is injected as a dependency — strategies do not hardcode any reduction logic.

The `Reducer` ABC provides:

| Method | Signature | Description |
|---|---|---|
| `reduce` | `(input: ReducerInput) -> str` | Produces a single reduced representation. Never raises. |

The `Reducer` is injected at strategy construction time by the consuming project.
`DefaultReducer` is used as the default when no reducer is configured.

The merger strategy is responsible for:
- Extracting `content` from each `DocumentChunk`
- Building the `ReducerInput` including any prompt template
- Calling `reducer.reduce(input)` to produce the parent node content

---

## Abstract Base: `BaseMergingStrategy`

All merging strategy implementations must extend this ABC. No defaults are provided —
every subclass must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this strategy handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(chunks: list[DocumentChunk]) -> bool` | Inspects the chunks to decide suitability. Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `BottomUpMergingStrategy` declares `1` |
| `merge` | `(chunks: list[DocumentChunk]) -> DocumentTree` | Produces a `DocumentTree` from the given chunks |

---

## Merger Registry

A `MergerRegistry` is instantiated by the consuming project and receives its strategy list
directly as a constructor argument.

**At startup**, the registry validates that no two registered strategies share the same
`get_priority()` for the same `FileType` — raises `MergerPriorityConflictError`, failing
fast before any document is merged.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Registry narrows candidates to strategies whose `supported_mime_types` includes the chunks' `FileType` |
| 2. `can_handle` | Each candidate inspects the chunk list |
| 3. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |

Raises `NoMergingStrategyFoundError` if no candidate survives steps 1–2. Under normal
operation this should never occur — it indicates a misconfiguration where
`BottomUpMergingStrategy` was omitted from the registered strategy list.

---

## `BottomUpMergingStrategy`

The default and only concrete merging strategy shipped with the module. Handles all
`FileType` values. Iteratively merges chunks bottom-up with a configurable branching
factor, calling `reducer.reduce()` at each level to produce parent node content.

| Attribute | Value |
|---|---|
| `supported_mime_types` | All `FileType` values including `UNKNOWN` |
| `get_priority()` | `1` |
| `can_handle` | Always `True` |
| Default `branching_factor` | `4` |
| Default `Reducer` | `DefaultReducer` |

### Algorithm

1. Build leaf nodes from each `DocumentChunk` — `level=0`, `chunk=chunk`, `content=chunk.content`
2. Group leaf nodes into batches of `branching_factor`
3. For each batch, extract `content` from each node, build a `ReducerInput`, call `reducer.reduce()` to produce parent content
4. Create a parent `TreeNode` at `level=1` with the reduced content and the batch as children
5. Repeat steps 2–4 on the parent nodes until a single root node remains
6. Return a `DocumentTree` with the root node

### Edge Cases

- A single chunk produces a tree with one leaf node as the root
- If the number of chunks is not divisible by `branching_factor`, the last batch is smaller

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Reduction | Injected via `Reducer` ABC |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── merger/
    ├── __init__.py
    ├── base.py                           # BaseMergingStrategy ABC
    ├── registry.py                       # MergerRegistry, errors
    └── implementations/
        ├── __init__.py
        └── bottom_up.py                  # BottomUpMergingStrategy
tests/
└── libs/
    └── merger/
        ├── test_registry.py
        └── implementations/
            └── test_bottom_up.py
```

---

## Implementation Order

1. `TreeNode` + `DocumentTree` (in `libs/common/models.py`)
2. `Reducer` ABC + `ReducerInput` + `DefaultReducer`
3. `BaseMergingStrategy` ABC
4. `MergerRegistry` + errors
5. `BottomUpMergingStrategy`
6. Tests at each stage

---

## Acceptance Criteria

- [ ] `TreeNode` dataclass defined with: `content`, `level`, `children`, `chunk`
- [ ] `TreeNode.source_reference` computed property returns leaf chunk reference or spanned range
- [ ] `DocumentTree` dataclass defined with: `root`, `mime_type`
- [ ] `BaseMergingStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `merge` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `MergerRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `MergerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoMergingStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`
- [ ] `BottomUpMergingStrategy` declares `supported_mime_types` covering all `FileType` values including `UNKNOWN`
- [ ] `BottomUpMergingStrategy` `can_handle` always returns `True`
- [ ] `BottomUpMergingStrategy` `get_priority` always returns `1`
- [ ] `BottomUpMergingStrategy` default `branching_factor` is `4`
- [ ] `BottomUpMergingStrategy` default `Reducer` is `DefaultReducer`
- [ ] `BottomUpMergingStrategy` builds leaf nodes from `DocumentChunk` objects at `level=0`
- [ ] `BottomUpMergingStrategy` calls `reducer.reduce()` at each merge level
- [ ] `BottomUpMergingStrategy` produces a single root node
- [ ] `BottomUpMergingStrategy` handles single chunk input — root is a leaf node
- [ ] `BottomUpMergingStrategy` handles last batch smaller than `branching_factor`
- [ ] Reducer injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoMergingStrategyFoundError`, tree structure correctness, level assignment, `source_reference` computation, single chunk edge case, reducer called at each level