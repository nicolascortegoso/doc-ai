# Parser Module

## Overview

A standalone, extensible document parsing library living at `libs/parser/` inside the
Document-AI project. Accepts raw file bytes and a `DocumentProfile` (produced by the
profiler) and produces a structured `ParsedDocument` dataclass. Designed around an ABC
and a priority-based registry so that format-specific extraction strategies can be added
incrementally without modifying the core module.

The `DefaultPageExtractionStrategy` ships as the only guaranteed fallback — it is the
baseline that all future strategies improve upon for their specific format and page type.

---

## Interface Contract

- **Input:** `bytes` — raw file content, `DocumentProfile` — profiler output
- **Output:** `ParsedDocument` — dataclass carrying per-page extracted text content

---

## Data Models

Defined in `libs/common/models.py` alongside `DocumentProfile` and `PageProfile`.

### `ParsedPage` Dataclass

Extracted content and metadata for a single page.

| Field | Type | Description |
|---|---|---|
| `page_number` | `int` | 1-based page number |
| `content` | `str` | Extracted text content for this page |
| `strategy` | `str` | Class name of the strategy that produced this page |

### `ParsedDocument` Dataclass

Top-level output of the parser.

| Field | Type | Description |
|---|---|---|
| `mime_type` | `FileType` | MIME type from the originating `DocumentProfile` |
| `page_count` | `int` | Total number of pages |
| `pages` | `list[ParsedPage]` | Per-page extracted content |

#### `to_markdown() -> str`

A utility method for debugging and/or storage purposes — not part of the pipeline.
Assembles the full document as a single Markdown string. Every page emits a
`<!-- page N -->` delimiter followed by its content, joined by `\n\n`. Empty pages
still emit their delimiter — page numbers remain consistent with the `DocumentProfile`.

```
doc.to_markdown()
# <!-- page 1 -->
# Page one content.
#
# <!-- page 2 -->
#
# <!-- page 3 -->
# Page three content.
```

---

## Text Cleaning

Text cleaning is injected as a dependency — strategies do not hardcode any cleaning logic.

### `TextCleaner` ABC

Defined in `libs/text/base.py`.

| Method | Signature | Description |
|---|---|---|
| `clean` | `(text: str) -> str` | Returns cleaned text. Never raises. |

### `PassthroughTextCleaner`

Defined in `libs/text/implementations/passthrough.py`. Returns text unchanged. Used as the
default when no real cleaner is configured.

Future implementations (e.g. `WhitespaceTextCleaner`, `MarkdownTextCleaner`) are added
under `libs/text/implementations/` without modifying any other code.

---

## Abstract Base: `BasePageExtractionStrategy`

All strategy implementations must extend this ABC. No defaults are provided — every subclass
must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this strategy handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(page_profile: PageProfile) -> bool` | Deep inspection of page profile (e.g. has text, not scanned). Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `DefaultPageExtractionStrategy` always declares `1` |
| `extract` | `(file_bytes: bytes, page_profile: PageProfile) -> str` | Extracts text content for the page. Returns empty string if no content can be extracted |

---

## Parser Registry

A `ParserRegistry` is instantiated by the consuming project and receives its strategy list
directly as a constructor argument. Text cleaner wiring is handled explicitly by the
consuming project at strategy construction time:

```python
registry = ParserRegistry(strategies=[
    PlainPdfExtractionStrategy(),
    DefaultPageExtractionStrategy(),
])
```

**At startup**, the registry validates that no two registered strategies share the same
`get_priority()` for the same `FileType` — raises `ParserPriorityConflictError`, failing
fast before any document is parsed.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Registry narrows candidates to strategies whose `supported_mime_types` includes the document's `FileType` |
| 2. `can_handle` | Each candidate inspects the `PageProfile` |
| 3. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner |
| 4. Record strategy | Winner's class name is stored on the resulting `ParsedPage` |

Raises `NoStrategyFoundError` if no candidate survives steps 1–2 for a given page. Under
normal operation this should never occur — it indicates a misconfiguration where
`DefaultPageExtractionStrategy` was omitted from the registered strategy list.

---

## `DefaultPageExtractionStrategy`

The guaranteed fallback strategy shipped with the module. Must be explicitly registered by
the consuming project like any other strategy. Declares all `FileType` values including
`FileType.UNKNOWN` in `supported_mime_types`, always returns `True` from `can_handle`, and
always declares priority `1` — ensuring it is always the last resort when no
higher-priority strategy matches.

Returns an empty string from `extract` — no content is extracted.
Does not require a `TextCleaner`.

---

## `PlainPdfExtractionStrategy`

Extracts plain text from text-based PDF pages using PyMuPDF. Handles only pages where
`has_text=True` and `is_scanned=False`. Text is passed through an injected `TextCleaner`
before being returned.

| Attribute | Value |
|---|---|
| `supported_mime_types` | `[FileType.PDF]` |
| `get_priority()` | `50` |
| `can_handle` | `page_profile.has_text and not page_profile.is_scanned` |
| Default `TextCleaner` | `PassthroughTextCleaner` |

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| PDF text extraction | `pymupdf` |
| Text cleaning | Injected via `TextCleaner` ABC — `PassthroughTextCleaner` by default |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
document-ai/
├── libs/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── enums.py                          # FileType, Layout
│   │   └── models.py                         # PageProfile, DocumentProfile, ParsedPage, ParsedDocument
│   ├── text/
│   │   ├── __init__.py
│   │   ├── base.py                           # TextCleaner ABC
│   │   └── implementations/
│   │       ├── __init__.py
│   │       └── passthrough.py                # PassthroughTextCleaner
│   └── parser/
│       ├── __init__.py
│       ├── base.py                           # BasePageExtractionStrategy ABC
│       ├── registry.py                       # ParserRegistry, errors
│       └── implementations/
│           ├── __init__.py
│           ├── default.py                    # DefaultPageExtractionStrategy
│           └── plain_pdf.py                  # PlainPdfExtractionStrategy
└── tests/
    └── libs/
        ├── text/
        │   └── implementations/
        │       └── test_passthrough.py
        └── parser/
            ├── test_models.py
            ├── test_registry.py
            └── implementations/
                ├── test_default.py
                └── test_plain_pdf.py
```

---

## Implementation Order

1. `ParsedPage` + `ParsedDocument` (added to `libs/common/models.py`)
2. `TextCleaner` ABC + `PassthroughTextCleaner`
3. `BasePageExtractionStrategy` ABC
4. `ParserRegistry` + errors
5. `DefaultPageExtractionStrategy`
6. `PlainPdfExtractionStrategy`
7. Tests at each stage

---

## Acceptance Criteria

- [ ] `ParsedPage` dataclass defined with: `page_number`, `content`, `strategy`
- [ ] `ParsedDocument` dataclass defined with: `mime_type`, `page_count`, `pages`
- [ ] `ParsedDocument.to_markdown()` available as a utility method for debugging and storage
- [ ] `ParsedDocument.to_markdown()` assembles full content with `<!-- page N -->` delimiters joined by `\n\n`
- [ ] `ParsedDocument.to_markdown()` emits delimiter for every page including empty ones
- [ ] `ParsedDocument.to_markdown()` returns empty string for document with no pages
- [ ] `TextCleaner` ABC defined with single abstract method `clean(text: str) -> str`
- [ ] `PassthroughTextCleaner` returns text unchanged, never raises
- [ ] `BasePageExtractionStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `extract` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `ParserRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `ParserPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`; documented as a misconfiguration signal
- [ ] `DefaultPageExtractionStrategy` declared with `supported_mime_types` covering all `FileType` values including `UNKNOWN`, `can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `DefaultPageExtractionStrategy` returns empty string from `extract`
- [ ] `DefaultPageExtractionStrategy` registered explicitly by the consuming project — no auto-registration logic in the registry
- [ ] `PlainPdfExtractionStrategy` handles only pages where `has_text=True` and `is_scanned=False`
- [ ] `PlainPdfExtractionStrategy` declares `supported_mime_types = [FileType.PDF]` and `get_priority() = 50`
- [ ] `PlainPdfExtractionStrategy` extracts text from the correct page by `page_number`
- [ ] `PlainPdfExtractionStrategy` passes extracted text through injected `TextCleaner`
- [ ] `PlainPdfExtractionStrategy` uses `PassthroughTextCleaner` when no cleaner is injected
- [ ] Text cleaner injected at strategy construction time by the consuming project
- [ ] Unit tests cover: registry conflict detection at startup, priority resolution, `can_handle` dispatch, `DefaultPageExtractionStrategy` as last resort, `NoStrategyFoundError` when default is omitted, `PassthroughTextCleaner` returns text unchanged, `PlainPdfExtractionStrategy` extracts correct page content, text cleaner called with extracted text
