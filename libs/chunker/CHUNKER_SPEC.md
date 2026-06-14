[← LIBS_SPEC](../LIBS_SPEC.md)

# Chunker Module

## Overview

Accepts a `ParsedDocument` and produces a list of `DocumentChunk` dataclasses. Designed
around an ABC and a priority-based registry so that format-specific chunking strategies
can be added incrementally without modifying the core module.

`SlidingWindowChunkingStrategy` ships as the only concrete implementation and serves as
the default last resort. It operates directly on `ParsedDocument.pages` — no serialisation
involved.

---

## Interface Contract

- **Input:** `ParsedDocument` — parser output
- **Output:** `list[DocumentChunk]` — list of self-contained text fragments with source references

---

## Split-Point Determination

Split-point determination is injected as a dependency — strategies do not hardcode any
splitting logic. See [SPLITTER_SPEC.md](splitter/SPLITTER_SPEC.md) for the full interface
contract.

The `Splitter` is injected at strategy construction time by the consuming project.
`CharacterSplitter` is used as the default when no splitter is configured.

---

## Abstract Base: `BaseChunkingStrategy`

All chunking strategy implementations must extend this ABC. No defaults are provided —
every subclass must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this strategy handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(document: ParsedDocument) -> bool` | Inspects the document to decide suitability. Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `SlidingWindowChunkingStrategy` declares `1` |
| `chunk` | `(document: ParsedDocument) -> list[DocumentChunk]` | Produces a list of `DocumentChunk` from the document |

---

## Chunker Registry

A `ChunkerRegistry` is instantiated by the consuming project and receives its strategy list
directly as a constructor argument.

**At startup**, the registry validates that no two registered strategies share the same
`get_priority()` for the same `FileType` — raises `ChunkerPriorityConflictError`, failing
fast before any document is chunked.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Registry narrows candidates to strategies whose `supported_mime_types` includes the document's `FileType` |
| 2. `can_handle` | Each candidate inspects the `ParsedDocument` |
| 3. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |

Raises `NoChunkingStrategyFoundError` if no candidate survives steps 1–2.

---

## `SlidingWindowChunkingStrategy`

The default and only concrete chunking strategy shipped with the module. Handles all
`FileType` values. Implements a sliding window directly over `ParsedDocument.pages`.
Accepts a `Splitter` injected at construction time to control where windows are cut.

| Attribute | Value |
|---|---|
| `supported_mime_types` | All `FileType` values including `UNKNOWN` |
| `get_priority()` | `1` |
| `can_handle` | Always `True` |
| Default `window_size` | `1000` characters |
| Default `overlap_ratio` | `0.2` |
| Default `Splitter` | `CharacterSplitter` |

### Algorithm

1. Concatenate `page.content` values from `ParsedDocument.pages` in order, building a
   **page map**: a list of `(char_position, page_number)` tuples
2. Slide a window of `window_size` characters over the concatenated text, advancing by
   `window_size * (1 - overlap_ratio)` characters each step
3. For each proposed window end position, call `splitter.find_split(text, end)` to
   determine the actual cut point
4. Resolve `page_start` and `page_end` from the page map
5. Produce a `DocumentChunk` per window

### Edge Cases

- Documents with no content produce an empty list
- A document shorter than `window_size` produces a single chunk
- The last window may be shorter than `window_size`

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Chunking unit | Characters |
| Overlap | Ratio of `window_size` |
| Split point | Injected via `Splitter` ABC |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── chunker/
    ├── __init__.py
    ├── base.py                           # BaseChunkingStrategy ABC
    ├── registry.py                       # ChunkerRegistry, errors
    ├── splitter/
    │   ├── __init__.py
    │   ├── base.py                       # Splitter ABC
    │   └── implementations/
    │       ├── __init__.py
    │       └── character.py              # CharacterSplitter
    └── implementations/
        ├── __init__.py
        └── sliding_window.py             # SlidingWindowChunkingStrategy
tests/
└── libs/
    └── chunker/
        ├── test_registry.py
        ├── splitter/
        │   └── implementations/
        │       └── test_character.py
        └── implementations/
            └── test_sliding_window.py
```

---

## Implementation Order

1. `Splitter` ABC + `CharacterSplitter`
2. `BaseChunkingStrategy` ABC
3. `ChunkerRegistry` + errors
4. `SlidingWindowChunkingStrategy`
5. Tests at each stage

---

## Acceptance Criteria

- [ ] `Splitter` ABC defined with single abstract method `find_split(text: str, position: int) -> int`
- [ ] `CharacterSplitter` returns `position` unchanged, never raises
- [ ] `BaseChunkingStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `chunk` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `ChunkerRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `ChunkerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoChunkingStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`
- [ ] `SlidingWindowChunkingStrategy` declares `supported_mime_types` covering all `FileType` values including `UNKNOWN`
- [ ] `SlidingWindowChunkingStrategy` `can_handle` always returns `True`
- [ ] `SlidingWindowChunkingStrategy` `get_priority` always returns `1`
- [ ] `SlidingWindowChunkingStrategy` default `window_size` is `1000`
- [ ] `SlidingWindowChunkingStrategy` default `overlap_ratio` is `0.2`
- [ ] `SlidingWindowChunkingStrategy` default `Splitter` is `CharacterSplitter`
- [ ] `SlidingWindowChunkingStrategy` operates directly on `ParsedDocument.pages`
- [ ] `SlidingWindowChunkingStrategy` builds a page map from concatenated page content
- [ ] `SlidingWindowChunkingStrategy` calls `splitter.find_split` to determine actual cut point per window
- [ ] `SlidingWindowChunkingStrategy` correctly resolves `page_start` and `page_end`
- [ ] `SlidingWindowChunkingStrategy` produces a single chunk for documents shorter than `window_size`
- [ ] `SlidingWindowChunkingStrategy` produces an empty list for documents with no content
- [ ] `SlidingWindowChunkingStrategy` records its class name on each `DocumentChunk.strategy`
- [ ] Splitter injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoChunkingStrategyFoundError`, sliding window correctness, overlap, page map resolution, `find_split` called per window, edge cases