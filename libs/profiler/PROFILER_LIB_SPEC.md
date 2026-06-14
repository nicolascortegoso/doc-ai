# Profiler Module

## Overview

Accepts raw file bytes and produces a structured `DocumentProfile` dataclass. Designed
around an ABC and a priority-based registry so that format-specific profilers can be added
incrementally without modifying the core module.

`DefaultProfiler` and `PdfProfiler` ship as the only concrete implementations.

---

## Interface Contract

- **Input:** `bytes` — raw file content
- **Output:** `DocumentProfile` — dataclass carrying document-level and page-level structural metadata

---

## Data Models

### `Layout` Enum

Describes the column layout detected on a page.

| Value | Description |
|---|---|
| `SINGLE_COLUMN` | Single column of text |
| `MULTI_COLUMN` | Two or more columns |
| `MIXED` | Combination of layouts on the same page |
| `UNKNOWN` | Could not be determined |

### `PageProfile` Dataclass

Structural metadata for a single page.

| Field | Type | Description |
|---|---|---|
| `page_number` | `int` | 1-based page number |
| `has_text` | `bool` | Page contains extractable text |
| `has_images` | `bool` | Page contains embedded images |
| `has_tables` | `bool` | Page contains tabular data |
| `is_scanned` | `bool` | Page appears to be a scanned image |
| `layout` | `Layout` | Detected column layout |
| `language` | `str | None` | Detected language as a locale code (e.g. `"en"`), or `None` if undetermined |

### `DocumentProfile` Dataclass

Top-level output of the profiler.

| Field | Type | Description |
|---|---|---|
| `mime_type` | `FileType` | MIME type resolved from magic bytes |
| `page_count` | `int` | Total number of pages |
| `pages` | `list[PageProfile]` | Per-page structural metadata |

---

## Detection

Detection concerns are handled by an injected `Detector` instance. The profiler does not
hardcode any detection strategy.

| Method | Signature | Description |
|---|---|---|
| `detect_language` | `(text: str) -> str` | Returns a locale code (e.g. `"en"`, `"fr"`). Never raises. |
| `detect_mime` | `(file_bytes: bytes) -> FileType` | Returns a `FileType` resolved from magic bytes. Never raises. |

The `Detector` is injected at construction time by the consuming project.

---

## Abstract Base: `BaseDocumentProfiler`

All profiler implementations must extend this ABC. No defaults are provided — every subclass
must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this profiler handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(file_bytes: bytes) -> bool` | Deep inspection of file content (encryption, version, internal structure). Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `DefaultProfiler` always declares `1` |
| `profile` | `(file_bytes: bytes) -> DocumentProfile` | Executes the profile and returns a populated `DocumentProfile` |

---

## Profiler Registry

A `ProfilerRegistry` is instantiated by the consuming project and receives its profiler
list and a `Detector` instance directly as constructor arguments. Detector wiring is
handled explicitly by the consuming project.

**At startup**, the registry validates that no two registered profilers share the same
`get_priority()` for the same `FileType` — raises `ProfilerPriorityConflictError`, failing
fast before any document is processed.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Detect MIME | Registry calls `detector.detect_mime(file_bytes)`, returns a `FileType` |
| 2. Filter by MIME | Registry narrows candidates to profilers whose `supported_mime_types` includes the detected `FileType` |
| 3. `can_handle` | Each candidate performs deep inspection of `file_bytes` |
| 4. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |

Raises `NoProfilerFoundError` if no candidate survives steps 2–3. Under normal operation
this should never occur — it indicates a misconfiguration where `DefaultProfiler` was
omitted from the registered profiler list.

---

## `DefaultProfiler`

Must be explicitly registered by the consuming project like any other profiler. Declares
all `FileType` values including `FileType.UNKNOWN` in `supported_mime_types`, always
returns `True` from `can_handle`, and always declares priority `1` — ensuring it is always
the last resort when no higher-priority profiler matches.

Returns:

```python
DocumentProfile(
    mime_type=FileType.UNKNOWN,
    page_count=0,
    pages=[],
)
```

Does not require a `Detector` — no text or MIME detection is performed.

---

## `PdfProfiler`

Profiles PDF documents using PyMuPDF. Accepts a `Detector` injected at construction time.

| Attribute | Value |
|---|---|
| `supported_mime_types` | `[FileType.PDF]` |
| `get_priority()` | `50` |
| `can_handle` | Returns `False` for encrypted PDFs, `True` otherwise |

Per-page profiling:

| Field | Logic |
|---|---|
| `has_text` | Page has extractable text |
| `has_images` | Page has embedded images |
| `has_tables` | `page.find_tables()` returns at least one table |
| `is_scanned` | No text but has images |
| `layout` | `SINGLE_COLUMN` if has text, `UNKNOWN` otherwise |
| `language` | `detector.detect_language(text)` if has text, `None` otherwise |

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| Detection | Injected via `Detector` ABC |
| PDF profiling | `pymupdf` |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── profiler/
    ├── __init__.py
    ├── base.py                           # BaseDocumentProfiler ABC
    ├── registry.py                       # ProfilerRegistry, errors
    └── implementations/
        ├── __init__.py
        ├── default.py                    # DefaultProfiler
        └── pdf.py                        # PdfProfiler
tests/
└── libs/
    └── profiler/
        ├── test_registry.py
        └── implementations/
            ├── test_default.py
            ├── test_pdf.py
            └── test_pdf_integration.py
```

---

## Implementation Order

1. `Layout` enum + `PageProfile` + `DocumentProfile` dataclasses (in `libs/common/`)
2. `BaseDocumentProfiler` ABC
3. `ProfilerRegistry` + errors
4. `DefaultProfiler`
5. `PdfProfiler`
6. Tests at each stage

---

## Acceptance Criteria

- [ ] `Layout` enum defined with `SINGLE_COLUMN`, `MULTI_COLUMN`, `MIXED`, `UNKNOWN`
- [ ] `PageProfile` dataclass defined with: `page_number`, `has_text`, `has_images`, `has_tables`, `is_scanned`, `layout`, `language`
- [ ] `DocumentProfile` dataclass defined with: `mime_type`, `page_count`, `pages`
- [ ] `BaseDocumentProfiler` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `profile` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `ProfilerRegistry` accepts profiler list and `Detector` as constructor arguments
- [ ] `ProfilerRegistry` calls `detector.detect_mime` for MIME detection
- [ ] `ProfilerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoProfilerFoundError` raised at runtime when no profiler survives MIME filtering + `can_handle`; documented as a misconfiguration signal
- [ ] `DefaultProfiler` declared with `supported_mime_types` covering all `FileType` values including `UNKNOWN`, `can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `DefaultProfiler` returns `DocumentProfile(mime_type=FileType.UNKNOWN, page_count=0, pages=[])`
- [ ] `DefaultProfiler` does not require a `Detector`
- [ ] `DefaultProfiler` registered explicitly by the consuming project — no auto-registration logic in the registry
- [ ] `PdfProfiler` accepts `Detector` at construction time
- [ ] `PdfProfiler` calls `detector.detect_language` per page
- [ ] `PdfProfiler` returns `False` from `can_handle` for encrypted PDFs
- [ ] Detector injected at construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection at startup, priority resolution, `can_handle` dispatch, `DefaultProfiler` as last resort, `NoProfilerFoundError` when `DefaultProfiler` is omitted, `PdfProfiler` per-page profiling, language detection called with page text