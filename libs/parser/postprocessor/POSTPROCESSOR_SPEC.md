[← PARSER_SPEC](../PARSER_SPEC.md)

# Postprocessor Module

## Overview

Provides a `Postprocessor` ABC for text post-processing. Injected into parser
strategies at construction time. Strategies do not hardcode any post-processing logic.

`PassthroughPostprocessor` ships as the only concrete implementation.

---

## Interface Contract

### `Postprocessor` ABC

Defined in `libs/parser/postprocessor/base.py`.

| Method | Signature | Description |
|---|---|---|
| `process` | `(text: str) -> str` | Processes extracted text. Never raises. |

---

## `PassthroughPostprocessor`

Defined in `libs/parser/postprocessor/implementations/passthrough.py`.

Returns the input text unchanged. Used as the default when no postprocessor
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
└── parser/
    └── postprocessor/
        ├── __init__.py
        ├── base.py                       # Postprocessor ABC
        └── implementations/
            ├── __init__.py
            └── passthrough.py            # PassthroughPostprocessor
tests/
└── test_libs/
    └── parser/
        └── postprocessor/
            └── implementations/
                └── test_passthrough.py
```

---

## Acceptance Criteria

- [ ] `Postprocessor` ABC defined with single abstract method `process(text: str) -> str`
- [ ] `process` never raises
- [ ] `PassthroughPostprocessor.process` returns input text unchanged
- [ ] Unit tests cover: returns text unchanged, never raises, empty string input