[← LIBS_SPEC](../LIBS_SPEC.md)

# Distiller Module

## Overview

Accepts a `ParsedDocument` and produces a list of `GlossaryEntry` objects by
extracting terms and definitions using an injected `Analyzer` (NLU) and an
injected `Composer` (NLG). Designed around an ABC and a priority-based registry
so that format-specific distillation strategies can be added incrementally.

`GlossaryDistillerStrategy` ships as the only concrete implementation.

---

## Interface Contract

- **Input:** `ParsedDocument` — parser output, `document_id: UUID` — originating document
- **Output:** `list[GlossaryEntry]` — extracted glossary entries with source traceability

---

## Extraction

Extraction is handled by an injected `Analyzer` instance — NLU concern.
See [ANALYZER_SPEC.md](analyzer/ANALYZER_SPEC.md) for the full interface contract.

The `Analyzer` is injected at strategy construction time by the consuming project.
`DefaultAnalyzer` is used when no analyzer is configured.

---

## Composition

Composition is handled by an injected `Composer` instance — NLG concern.
See [COMPOSER_SPEC.md](composer/COMPOSER_SPEC.md) for the full interface contract.

The `Composer` is injected at strategy construction time by the consuming project.
`DefaultComposer` is used when no composer is configured.

---

## Abstract Base: `BaseDistillerStrategy`

All distiller strategy implementations must extend this ABC. No defaults are
provided — every subclass must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this strategy handles |
| `can_handle` | `(document: ParsedDocument) -> bool` | Inspects the document to decide suitability |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 |
| `distill` | `(document: ParsedDocument, document_id: UUID) -> list[GlossaryEntry]` | Produces glossary entries from the document |

---

## Distiller Registry

A `DistillerRegistry` is instantiated by the consuming project and receives its
strategy list directly as a constructor argument.

**At startup**, the registry validates that no two registered strategies share the
same `get_priority()` for the same `FileType` — raises `DistillerPriorityConflictError`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Registry narrows candidates by `supported_mime_types` |
| 2. `can_handle` | Each candidate inspects the `ParsedDocument` |
| 3. Sort & dispatch | Registry dispatches to the highest-priority surviving candidate |

Raises `NoDistillerStrategyFoundError` if no candidate survives steps 1–2.

---

## `GlossaryDistillerStrategy`

Extracts glossary entries from a `ParsedDocument` by:
1. Iterating over each `ParsedPage`
2. Calling `analyzer.analyze()` to extract terms and definitions
3. Calling `composer.compose()` to refine and format each entry
4. Returning a `list[GlossaryEntry]` with `document_id` stamped on each entry

| Attribute | Value |
|---|---|
| `supported_mime_types` | All `FileType` values including `UNKNOWN` |
| `get_priority()` | `1` |
| `can_handle` | Always `True` |
| Default `Analyzer` | `DefaultAnalyzer` |
| Default `Composer` | `DefaultComposer` |

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
libs/
└── distiller/
    ├── __init__.py
    ├── base.py                           # BaseDistillerStrategy ABC
    ├── registry.py                       # DistillerRegistry, errors
    ├── analyzer/
    │   ├── __init__.py
    │   ├── base.py                       # Analyzer ABC
    │   ├── models.py                     # AnalyzerInput
    │   └── implementations/
    │       ├── __init__.py
    │       └── default.py               # DefaultAnalyzer
    ├── composer/
    │   ├── __init__.py
    │   ├── base.py                       # Composer ABC
    │   ├── models.py                     # ComposerInput
    │   └── implementations/
    │       ├── __init__.py
    │       └── default.py               # DefaultComposer
    └── implementations/
        ├── __init__.py
        └── glossary.py                  # GlossaryDistillerStrategy
tests/
└── test_libs/
    └── distiller/
        ├── test_registry.py
        ├── analyzer/
        │   └── implementations/
        │       └── test_default.py
        ├── composer/
        │   └── implementations/
        │       └── test_default.py
        └── implementations/
            └── test_glossary.py
```

---

## Implementation Order

1. `GlossaryEntry` dataclass in `common/models.py`
2. `Analyzer` ABC + `AnalyzerInput` + `DefaultAnalyzer`
3. `Composer` ABC + `ComposerInput` + `DefaultComposer`
4. `BaseDistillerStrategy` ABC
5. `DistillerRegistry` + errors
6. `GlossaryDistillerStrategy`
7. Tests at each stage

---

## Acceptance Criteria

- [ ] `GlossaryEntry` dataclass defined in `common/models.py` with: `term`, `slug`, `definition`, `evidence`, `document_id`
- [ ] `BaseDistillerStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `distill` all abstract
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `DistillerRegistry` accepts strategy list as constructor argument, runs conflict detection at startup
- [ ] `DistillerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoDistillerStrategyFoundError` raised at runtime when no strategy survives filtering
- [ ] `GlossaryDistillerStrategy` declares `supported_mime_types` covering all `FileType` values
- [ ] `GlossaryDistillerStrategy` `can_handle` always returns `True`
- [ ] `GlossaryDistillerStrategy` `get_priority` always returns `1`
- [ ] `GlossaryDistillerStrategy` stamps `document_id` on every `GlossaryEntry`
- [ ] `GlossaryDistillerStrategy` calls `analyzer.analyze()` per page
- [ ] `GlossaryDistillerStrategy` calls `composer.compose()` per extracted term
- [ ] Analyzer and Composer injected at strategy construction time
- [ ] Unit tests cover: registry conflict detection, priority resolution, `can_handle` dispatch, `NoDistillerStrategyFoundError`, glossary entry production, `document_id` stamping