# Postprocessor Module

## Overview

Provides a `Postprocessor` ABC for text post-processing concerns — transforming, cleaning,
or enriching extracted text content. Designed for dependency injection so that consuming
modules remain decoupled from any specific post-processing implementation.

`PassthroughPostprocessor` ships as the only concrete implementation.

---

## Interface Contract

### `Postprocessor` ABC

Defined in `libs/postprocessor/base.py`.

| Method | Signature | Description |
|---|---|---|
| `process` | `(text: str) -> str` | Transforms the given text. Returns the processed string. Never raises. |

The method is abstract — every implementation must explicitly declare it.

---

## `PassthroughPostprocessor`

Defined in `libs/postprocessor/implementations/passthrough.py`.

| Method | Behaviour |
|---|---|
| `process` | Returns text unchanged. Used as the default when no real postprocessor is configured. |

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
└── postprocessor/
    ├── __init__.py
    ├── base.py                       # Postprocessor ABC
    └── implementations/
        ├── __init__.py
        └── passthrough.py            # PassthroughPostprocessor
tests/
└── libs/
    └── postprocessor/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_passthrough.py
```

---

## Implementation Order

1. `Postprocessor` ABC
2. `PassthroughPostprocessor`
3. Tests

---

## Acceptance Criteria

- [ ] `Postprocessor` ABC defined with single abstract method `process(text: str) -> str`
- [ ] `process(text: str) -> str` — returns processed string, never raises
- [ ] `PassthroughPostprocessor` implements `process`
- [ ] `PassthroughPostprocessor.process` returns text unchanged
- [ ] `PassthroughPostprocessor.process` never raises
- [ ] Injected at construction time by the consuming project — no auto-instantiation
- [ ] Unit tests cover: `process` returns text unchanged, `process` never raises
