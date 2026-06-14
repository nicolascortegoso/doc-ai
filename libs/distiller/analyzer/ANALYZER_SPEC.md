[← DISTILLER_SPEC](../DISTILLER_SPEC.md)

# Analyzer Module

## Overview

Provides an `Analyzer` ABC for natural language understanding (NLU). Injected
into distiller strategies at construction time. Strategies do not hardcode any
extraction logic.

The `Analyzer` reads document content and extracts structured information
according to an instruction — terms, definitions, entities, or any other
structured knowledge.

`DefaultAnalyzer` ships as the only concrete implementation.

---

## Data Models

### `AnalyzerInput` Dataclass

Defined in `libs/distiller/analyzer/models.py`.

| Field | Type | Description |
|---|---|---|
| `content` | `str` | Document text to analyze |
| `instruction` | `str` | What to extract from the content |
| `context` | `dict | None` | Optional additional context |

---

## Interface Contract

### `Analyzer` ABC

Defined in `libs/distiller/analyzer/base.py`.

| Method | Signature | Description |
|---|---|---|
| `analyze` | `(input: AnalyzerInput) -> str` | Analyze content and return extracted information as a string. Never raises. |

---

## `DefaultAnalyzer`

Defined in `libs/distiller/analyzer/implementations/default.py`.

Returns an empty string. Used as the no-op default when no real analyzer
is configured.

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
    └── analyzer/
        ├── __init__.py
        ├── base.py                       # Analyzer ABC
        ├── models.py                     # AnalyzerInput
        └── implementations/
            ├── __init__.py
            └── default.py               # DefaultAnalyzer
tests/
└── test_libs/
    └── distiller/
        └── analyzer/
            └── implementations/
                └── test_default.py
```

---

## Acceptance Criteria

- [ ] `AnalyzerInput` dataclass defined with: `content`, `instruction`, `context`
- [ ] `context` is optional, defaulting to `None`
- [ ] `Analyzer` ABC defined with single abstract method `analyze(input: AnalyzerInput) -> str`
- [ ] `analyze` never raises
- [ ] `DefaultAnalyzer.analyze` returns empty string
- [ ] Unit tests cover: `AnalyzerInput` construction, `analyze` returns empty string, never raises