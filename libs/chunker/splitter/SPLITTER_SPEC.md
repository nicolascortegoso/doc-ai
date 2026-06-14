[← CHUNKER_SPEC](../CHUNKER_SPEC.md)

# Splitter Module

## Overview

Provides a `Splitter` ABC for split-point determination. Injected into chunking
strategies at construction time. Strategies do not hardcode any splitting logic.

`CharacterSplitter` ships as the only concrete implementation.

---

## Interface Contract

### `Splitter` ABC

Defined in `libs/chunker/splitter/base.py`.

| Method | Signature | Description |
|---|---|---|
| `find_split` | `(text: str, position: int) -> int` | Returns the actual split position given a proposed position. Never raises. |

---

## `CharacterSplitter`

Defined in `libs/chunker/splitter/implementations/character.py`.

Returns `position` unchanged — splits exactly at the proposed character position.
Used as the default when no splitter is configured.

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
└── chunker/
    └── splitter/
        ├── __init__.py
        ├── base.py                       # Splitter ABC
        └── implementations/
            ├── __init__.py
            └── character.py              # CharacterSplitter
tests/
└── libs/
    └── chunker/
        └── splitter/
            └── implementations/
                └── test_character.py
```

---

## Acceptance Criteria

- [ ] `Splitter` ABC defined with single abstract method `find_split(text: str, position: int) -> int`
- [ ] `find_split` never raises
- [ ] `CharacterSplitter.find_split` returns `position` unchanged
- [ ] Unit tests cover: returns position unchanged, never raises