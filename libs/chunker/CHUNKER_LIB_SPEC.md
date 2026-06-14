# Chunker Module

## Overview

Accepts a `ParsedDocument` and produces a list of `DocumentChunk` dataclasses. Designed
around an ABC and a priority-based registry so that format-specific chunking strategies
can be added incrementally without modifying the core module.

`SlidingWindowChunkingStrategy` ships as the only concrete implementation and serves as
the default last resort. It operates directly on `ParsedDocument.pages` — no serialisation
involved. Each `ParsedPage` carries `page_number` and `content`, giving the chunker
everything it needs to produce self-contained `DocumentChunk` objects with accurate
`SourceReference` values.

---

## Interface Contract

- **Input:** `ParsedDocument` — parser output
- **Output:** `list[DocumentChunk]` — list of self-contained text fragments with source references

---

## Data Models

Defined in `libs/common/models.py`.

### `SourceReference` Dataclass

Citation anchor for a `DocumentChunk`.

| Field | Type | Description |
|---|---|---|
| `page_start` | `int` | 1-based page number where the chunk begins |
| `page_end` | `int` | 1-based page number where the chunk ends |

### `DocumentChunk` Dataclass

A self-contained fragment of a document.

| Field | Type | Description |
|---|---|---|
| `content` | `str` | Extracted text content of the chunk |
| `source_reference` | `SourceReference` | Citation anchor |
| `mime_type` | `FileType` | MIME type from the originating `ParsedDocument` |
| `strategy` | `str` | Class name of the strategy that produced this chunk |

---

## Split-Point Determination

Split-point determination is injected as a dependency — strategies do not hardcode any
splitting logic.

The `Splitter` ABC provides:

| Method | Signature | Description |
|---|---|---|
| `find_split` | `(text: str, position: int) -> int` | Given a desired split position, returns the actual position to cut at. Never raises. |

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

Raises `NoChunkingStrategyFoundError` if no candidate survives steps 1–2. Under normal
operation this should never occur — it indicates a misconfiguration where
`SlidingWindowChunkingStrategy` was omitted from the registered strategy list.

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
   **page map**: a list of `(char_position, page_number)` tuples marking where each page
   begins in the concatenated text
2. Slide a window of `window_size` characters over the concatenated text, advancing by
   `window_size * (1 - overlap_ratio)` characters each step
3. For each proposed window end position, call `splitter.find_split(text, end)` to
   determine the actual cut point
4. Resolve `page_start` and `page_end` from the page map using the window's start and
   actual end positions
5. Produce a `DocumentChunk` per window

### Page Map

The page map is built during concatenation. Each entry records the character position in
the concatenated text where a page's content begins, paired with its page number. Window
positions are resolved against this map to populate `SourceReference`.

### Overlap

Overlap is expressed as a ratio of `window_size`. With `window_size=1000` and
`overlap_ratio=0.2`, the window advances 800 characters per step and the last 200
characters of each chunk are repeated at the start of the next.

### Edge Cases

- Documents with no content (all pages empty) produce an empty list
- A document shorter than `window_size` produces a single chunk
- The last window may be shorter than `window_size` if the remaining text is shorter

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
    └── implementations/
        ├── __init__.py
        └── sliding_window.py             # SlidingWindowChunkingStrategy
tests/
└── libs/
    └── chunker/
        ├── test_registry.py
        └── implementations/
            └── test_sliding_window.py
```

---

## Implementation Order

1. `SourceReference` + `DocumentChunk` (in `libs/common/models.py`)
2. `Splitter` ABC + `CharacterSplitter`
3. `BaseChunkingStrategy` ABC
4. `ChunkerRegistry` + errors
5. `SlidingWindowChunkingStrategy`
6. Tests at each stage

---

## Acceptance Criteria

- [ ] `SourceReference` dataclass defined with: `page_start`, `page_end`
- [ ] `DocumentChunk` dataclass defined with: `content`, `source_reference`, `mime_type`, `strategy`
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
- [ ] `SlidingWindowChunkingStrategy` correctly resolves `page_start` and `page_end` for chunks within a single page
- [ ] `SlidingWindowChunkingStrategy` correctly resolves `page_start` and `page_end` for chunks spanning multiple pages
- [ ] `SlidingWindowChunkingStrategy` advances window by `window_size * (1 - overlap_ratio)` characters per step
- [ ] `SlidingWindowChunkingStrategy` produces a single chunk for documents shorter than `window_size`
- [ ] `SlidingWindowChunkingStrategy` produces an empty list for documents with no content
- [ ] `SlidingWindowChunkingStrategy` records its class name on each `DocumentChunk.strategy`
- [ ] Splitter injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoChunkingStrategyFoundError`, sliding window correctness, overlap, page map resolution, `find_split` called per window, edge cases