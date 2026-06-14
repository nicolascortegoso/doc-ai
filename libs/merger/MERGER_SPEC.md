[← LIBS_SPEC](../LIBS_SPEC.md)

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

## Reduction

Reduction is injected as a dependency — strategies do not hardcode any reduction logic.
See [REDUCER_SPEC.md](reducer/REDUCER_SPEC.md) for the full interface contract.

The `Reducer` is injected at strategy construction time by the consuming project.
`TruncatingReducer` is used as the default when no reducer is configured.

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

Raises `NoMergingStrategyFoundError` if no candidate survives steps 1–2.

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
| Default `Reducer` | `TruncatingReducer` |

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
    ├── reducer/
    │   ├── __init__.py
    │   ├── base.py                       # Reducer ABC
    │   ├── models.py                     # ReducerInput
    │   └── implementations/
    │       ├── __init__.py
    │       └── truncating.py             # TruncatingReducer
    └── implementations/
        ├── __init__.py
        └── bottom_up.py                  # BottomUpMergingStrategy
tests/
└── libs/
    └── merger/
        ├── test_registry.py
        ├── reducer/
        │   ├── test_models.py
        │   └── implementations/
        │       └── test_truncating.py
        └── implementations/
            └── test_bottom_up.py
```

---

## Implementation Order

1. `Reducer` ABC + `ReducerInput` + `TruncatingReducer`
2. `BaseMergingStrategy` ABC
3. `MergerRegistry` + errors
4. `BottomUpMergingStrategy`
5. Tests at each stage

---

## Acceptance Criteria

- [ ] `Reducer` ABC defined with single abstract method `reduce(input: ReducerInput) -> str`
- [ ] `ReducerInput` dataclass defined with: `texts`, `prompt_template`, `context`
- [ ] `TruncatingReducer` truncates each text to `max_chars_per_text` and joins with a space
- [ ] `BaseMergingStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `merge` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `MergerRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `MergerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoMergingStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`
- [ ] `BottomUpMergingStrategy` declares `supported_mime_types` covering all `FileType` values including `UNKNOWN`
- [ ] `BottomUpMergingStrategy` `can_handle` always returns `True`
- [ ] `BottomUpMergingStrategy` `get_priority` always returns `1`
- [ ] `BottomUpMergingStrategy` default `branching_factor` is `4`
- [ ] `BottomUpMergingStrategy` default `Reducer` is `TruncatingReducer`
- [ ] `BottomUpMergingStrategy` builds leaf nodes from `DocumentChunk` objects at `level=0`
- [ ] `BottomUpMergingStrategy` calls `reducer.reduce()` at each merge level
- [ ] `BottomUpMergingStrategy` produces a single root node
- [ ] `BottomUpMergingStrategy` handles single chunk input
- [ ] `BottomUpMergingStrategy` handles last batch smaller than `branching_factor`
- [ ] Reducer injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoMergingStrategyFoundError`, tree structure correctness, level assignment, `source_reference` computation, single chunk edge case, reducer called at each level