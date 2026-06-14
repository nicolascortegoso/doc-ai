[← MERGER_SPEC](../MERGER_SPEC.md)

# Reducer Module

## Overview

Provides a `Reducer` ABC for text reduction. Injected into merging strategies at
construction time. Strategies do not hardcode any reduction logic.

`TruncatingReducer` ships as the only concrete implementation.

---

## Data Models

### `ReducerInput` Dataclass

Defined in `libs/merger/reducer/models.py`.

| Field | Type | Description |
|---|---|---|
| `texts` | `list[str]` | List of text inputs to reduce |
| `prompt_template` | `str | None` | Optional prompt template for LLM-based implementations |
| `context` | `dict | None` | Optional additional context for the reducer |

---

## Interface Contract

### `Reducer` ABC

Defined in `libs/merger/reducer/base.py`.

| Method | Signature | Description |
|---|---|---|
| `reduce` | `(input: ReducerInput) -> str` | Produces a single reduced representation. Never raises. |

---

## `TruncatingReducer`

Defined in `libs/merger/reducer/implementations/truncating.py`.

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
└── merger/
    └── reducer/
        ├── __init__.py
        ├── base.py                       # Reducer ABC
        ├── models.py                     # ReducerInput
        └── implementations/
            ├── __init__.py
            └── truncating.py             # TruncatingReducer
tests/
└── libs/
    └── merger/
        └── reducer/
            ├── test_models.py
            └── implementations/
                └── test_truncating.py
```

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
- [ ] Unit tests cover: `ReducerInput` construction, truncation, joining, output length constraint, never raises