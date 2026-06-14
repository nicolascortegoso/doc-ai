[← DISTILLER_SPEC](../DISTILLER_SPEC.md)

# Composer Module

## Overview

Provides a `Composer` ABC for natural language generation (NLG). Injected
into distiller strategies at construction time. Strategies do not hardcode any
composition logic.

The `Composer` takes extracted knowledge and composes structured, readable
output — refining raw extractions into well-formed definitions, summaries,
or other structured content.

`DefaultComposer` ships as the only concrete implementation.

---

## Data Models

### `ComposerInput` Dataclass

Defined in `libs/distiller/composer/models.py`.

| Field | Type | Description |
|---|---|---|
| `content` | `str` | Extracted knowledge to compose |
| `instruction` | `str` | How to compose the output |
| `context` | `dict | None` | Optional additional context |

---

## Interface Contract

### `Composer` ABC

Defined in `libs/distiller/composer/base.py`.

| Method | Signature | Description |
|---|---|---|
| `compose` | `(input: ComposerInput) -> str` | Compose structured output from extracted knowledge. Never raises. |

---

## `DefaultComposer`

Defined in `libs/distiller/composer/implementations/default.py`.

Returns an empty string. Used as the no-op default when no real composer
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
    └── composer/
        ├── __init__.py
        ├── base.py                       # Composer ABC
        ├── models.py                     # ComposerInput
        └── implementations/
            ├── __init__.py
            └── default.py               # DefaultComposer
tests/
└── test_libs/
    └── distiller/
        └── composer/
            └── implementations/
                └── test_default.py
```

---

## Acceptance Criteria

- [ ] `ComposerInput` dataclass defined with: `content`, `instruction`, `context`
- [ ] `context` is optional, defaulting to `None`
- [ ] `Composer` ABC defined with single abstract method `compose(input: ComposerInput) -> str`
- [ ] `compose` never raises
- [ ] `DefaultComposer.compose` returns empty string
- [ ] Unit tests cover: `ComposerInput` construction, `compose` returns empty string, never raises