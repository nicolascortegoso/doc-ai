# Reducer Module

## Overview

Provides a `Reducer` ABC for text reduction concerns — taking multiple text inputs and
producing a single reduced representation. Designed for dependency injection so that
consuming modules remain decoupled from any specific reduction implementation.

`TruncatingReducer` ships as the only concrete implementation.

---

## Data Models

### `ReducerInput` Dataclass

Defined in `libs/reducer/models.py`.

| Field | Type | Description |
|---|---|---|
| `texts` | `list[str]` | List of text inputs to reduce |
| `prompt_template` | `str | None` | Optional prompt template for LLM-based implementations |
| `context` | `dict | None` | Optional additional context for the reducer |

---

## Interface Contract

### `Reducer` ABC

Defined in `libs/reducer/base.py`.

| Method | Signature | Description |
|---|---|---|
| `reduce` | `(input: ReducerInput) -> str` | Produces a single reduced representation from the input. Never raises. |

The method is abstract — every implementation must explicitly declare it.

---

## `TruncatingReducer`

Defined in `libs/reducer/implementations/default.py`.

Truncates each text in `input.texts` to `max_chars_per_text` characters and joins
them with a space. Produces a genuinely reduced output without requiring an LLM.

| Parameter | Default | Description |
|---|---|---|
| `max_chars_per_text` | `200` | Maximum characters to retain from each input text |

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
└── reducer/
    ├── __init__.py
    ├── base.py                       # Reducer ABC
    ├── models.py                     # ReducerInput
    └── implementations/
        ├── __init__.py
        └── default.py                # TruncatingReducer
tests/
└── libs/
    └── reducer/
        ├── __init__.py
        ├── test_models.py
        └── implementations/
            ├── __init__.py
            └── test_default.py
```

---

## Implementation Order

1. `ReducerInput` dataclass
2. `Reducer` ABC
3. `TruncatingReducer`
4. Tests

---

## Acceptance Criteria

- [ ] `ReducerInput` dataclass defined with: `texts`, `prompt_template`, `context`
- [ ] `prompt_template` and `context` are optional, defaulting to `None`
- [ ] `Reducer` ABC defined with single abstract method `reduce(input: ReducerInput) -> str`
- [ ] `reduce` never raises
- [ ] `TruncatingReducer` accepts `max_chars_per_text` at construction time, defaults to `200`
- [ ] `TruncatingReducer.reduce` truncates each text to `max_chars_per_text` characters
- [ ] `TruncatingReducer.reduce` joins truncated texts with a space
- [ ] `TruncatingReducer.reduce` output is shorter than or equal to the combined input length
- [ ] `TruncatingReducer.reduce` never raises
- [ ] Injected at construction time by the consuming project — no auto-instantiation
- [ ] Unit tests cover: `ReducerInput` construction, `reduce` truncates correctly, `reduce` joins correctly, `reduce` never raises, output length constraint