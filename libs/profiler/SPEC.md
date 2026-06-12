# Profiler Module

## Overview

A standalone, extensible document profiling library living at `libs/profiler/` inside the
Document-AI project. Accepts raw file bytes and produces a structured `DocumentProfile`
dataclass. Designed around an ABC and a priority-based registry so that format-specific
profilers can be added incrementally without modifying the core module.

The `DefaultProfiler` ships as the only concrete implementation — it is the baseline that all
future profilers improve upon for their specific format.

---

## Interface Contract

- **Input:** `bytes` — raw file content
- **Output:** `DocumentProfile` — dataclass carrying document-level and page-level structural metadata

---

## `FileType` Enum

Centralises all supported MIME types. Used throughout the module to avoid raw strings.

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

## Language Detection

Language detection is injected as a dependency — the profiler does not hardcode any
detection strategy.

### `LanguageDetector` ABC

Defined in `libs/language/base.py`.

| Method | Signature | Description |
|---|---|---|
| `detect` | `(text: str) -> str` | Returns a locale code (e.g. `"en"`, `"fr"`). Never raises. |

### `DummyLanguageDetector`

Defined in `libs/language/implementations/dummy.py`. Always returns `"en"`. Used as the
default when no real detector is configured.

Future implementations (e.g. `LinguaLanguageDetector`) are added under
`libs/language/implementations/` without modifying any other code.

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

## `MimeTypeDetector` Utility

Defined in `libs/profiler/detector.py`. Magic-byte inspection via `python-magic`. Returns a `FileType`. Returns
`FileType.UNKNOWN` for unrecognised signatures — never raises.

MIME detection ownership lives in this module.

---

## Profiler Registry

A `ProfilerRegistry` is instantiated by the consuming project and receives its profiler list
directly as a constructor argument. Language detector wiring is handled explicitly by the
consuming project:

```python
detector = DummyLanguageDetector()

registry = ProfilerRegistry(profilers=[
    PdfProfiler(language_detector=detector),
    DefaultProfiler(),
])
```

**At startup**, the registry validates that no two registered profilers share the same
`get_priority()` for the same `FileType` — raises `ProfilerPriorityConflictError`, failing
fast before any document is processed.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Detect MIME | Registry delegates to `MimeTypeDetector`, returns a `FileType` |
| 2. Filter by MIME | Registry narrows candidates to profilers whose `supported_mime_types` includes the detected `FileType` |
| 3. `can_handle` | Each candidate performs deep inspection of `file_bytes` |
| 4. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |

Raises `NoProfilerFoundError` if no candidate survives steps 2–3. Under normal operation
this should never occur — it indicates a misconfiguration where `DefaultProfiler` was omitted
from the registered profiler list.

---

## `DefaultProfiler`

The only concrete profiler shipped with the module. Must be explicitly registered by the
consuming project like any other profiler. Declares all `FileType` values including
`FileType.UNKNOWN` in `supported_mime_types`, always returns `True` from `can_handle`, and
always declares priority `1` — ensuring it is always the last resort when no higher-priority
profiler matches.

Returns:

```python
DocumentProfile(
    mime_type=FileType.UNKNOWN,
    page_count=0,
    pages=[],
)
```

Does not require a `LanguageDetector` — no text is extracted.

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| MIME detection | `python-magic` + `libmagic` system dependency |
| Language detection | Injected via `LanguageDetector` ABC — `DummyLanguageDetector` by default |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
document-ai/
├── libs/
│   ├── language/
│   │   ├── __init__.py
│   │   ├── base.py                       # LanguageDetector ABC
│   │   └── implementations/
│   │       ├── __init__.py
│   │       └── dummy.py                  # DummyLanguageDetector
│   └── profiler/
│       ├── __init__.py
│       ├── enums.py                      # FileType enum
│       ├── models.py                     # DocumentProfile, PageProfile, Layout
│       ├── base.py                       # BaseDocumentProfiler ABC
│       ├── detector.py                   # MimeTypeDetector
│       ├── registry.py                   # ProfilerRegistry, errors
│       └── implementations/
│           ├── __init__.py
│           └── default.py                # DefaultProfiler
└── tests/
    └── libs/
        ├── language/
        │   └── implementations/
        │       └── test_dummy.py
        └── profiler/
            ├── test_detector.py
            ├── test_registry.py
            └── implementations/
                └── test_default.py
```

---

## Implementation Order

1. `FileType` enum + `Layout` enum
2. `PageProfile` + `DocumentProfile` dataclasses
3. `LanguageDetector` ABC + `DummyLanguageDetector`
4. `BaseDocumentProfiler` ABC
5. `MimeTypeDetector`
6. `ProfilerRegistry` + errors
7. `DefaultProfiler`
8. Tests at each stage

---

## Acceptance Criteria

- [ ] `FileType` enum defined with all supported MIME types plus `FileType.UNKNOWN`
- [ ] `Layout` enum defined with `SINGLE_COLUMN`, `MULTI_COLUMN`, `MIXED`, `UNKNOWN`
- [ ] `PageProfile` dataclass defined with: `page_number`, `has_text`, `has_images`, `has_tables`, `is_scanned`, `layout`, `language`
- [ ] `DocumentProfile` dataclass defined with: `mime_type`, `page_count`, `pages`
- [ ] `LanguageDetector` ABC defined with single abstract method `detect(text: str) -> str`
- [ ] `DummyLanguageDetector` always returns `"en"`, never raises
- [ ] `BaseDocumentProfiler` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `profile` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `MimeTypeDetector` implemented using `python-magic`, returns `FileType`, returns `FileType.UNKNOWN` for unrecognised signatures — never raises
- [ ] `ProfilerRegistry` accepts profiler list as constructor argument, runs conflict detection at startup
- [ ] `ProfilerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoProfilerFoundError` raised at runtime when no profiler survives MIME filtering + `can_handle`; documented as a misconfiguration signal
- [ ] `DefaultProfiler` declared with `supported_mime_types` covering all `FileType` values including `UNKNOWN`, `can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `DefaultProfiler` returns `DocumentProfile(mime_type=FileType.UNKNOWN, page_count=0, pages=[])`
- [ ] `DefaultProfiler` registered explicitly by the consuming project — no auto-registration logic in the registry
- [ ] Language detector injected at profiler construction time by the consuming project
- [ ] Unit tests cover: `MimeTypeDetector` correct detection and `FileType.UNKNOWN` fallback, registry conflict detection at startup, priority resolution, `can_handle` dispatch, `DefaultProfiler` as last resort, `NoProfilerFoundError` when `DefaultProfiler` is omitted, `DummyLanguageDetector` always returns `"en"`
