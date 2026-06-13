# Splitter Module

## Overview

Provides a `Splitter` ABC for text split-point determination. Designed for dependency
injection so that consuming modules remain decoupled from any specific splitting
implementation.

`CharacterSplitter` ships as the only concrete implementation.

---

## Interface Contract

### `Splitter` ABC

Defined in `libs/splitter/base.py`.

| Method | Signature | Description |
|---|---|---|
| `find_split` | `(text: str, position: int) -> int` | Given a desired split position, returns the actual position to cut at. The returned position must be in the range [0, len(text)]. Never raises. |

The method is abstract — every implementation must explicitly declare it.

---

## `CharacterSplitter`

Defined in `libs/splitter/implementations/character.py`.

| Method | Behaviour |
|---|---|
| `find_split` | Returns `position` unchanged — cuts at the exact character boundary. |

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
└── splitter/
    ├── __init__.py
    ├── base.py                       # Splitter ABC
    └── implementations/
        ├── __init__.py
        └── character.py              # CharacterSplitter
tests/
└── libs/
    └── splitter/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_character.py
```

---

## Implementation Order

1. `Splitter` ABC
2. `CharacterSplitter`
3. Tests

---

## Acceptance Criteria

- [ ] `Splitter` ABC defined with single abstract method `find_split(text: str, position: int) -> int`
- [ ] `find_split` returns a position in the range [0, len(text)], never raises
- [ ] `CharacterSplitter` implements `find_split`
- [ ] `CharacterSplitter.find_split` returns `position` unchanged
- [ ] `CharacterSplitter.find_split` never raises
- [ ] Injected at construction time by the consuming project — no auto-instantiation
- [ ] Unit tests cover: `find_split` returns position unchanged, `find_split` never raises