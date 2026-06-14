# Embedder Module

## Overview

Provides an `Embedder` ABC for text-to-vector transformation. Designed for dependency
injection so that consuming modules remain decoupled from any specific embedding
implementation.

`RandomEmbedder` ships as the only concrete implementation.

---

## Interface Contract

### `Embedder` ABC

Defined in `libs/embedder/base.py`.

| Method/Property | Signature | Description |
|---|---|---|
| `dimension` | `int` (property) | The dimensionality of the produced embeddings |
| `embed` | `(text: str) -> list[float]` | Embed a single text. Never raises. |
| `embed_batch` | `(texts: list[str]) -> list[list[float]]` | Embed multiple texts. Returns one embedding per input text. Never raises. |

All methods are abstract — every implementation must explicitly declare them.

---

## `RandomEmbedder`

Defined in `libs/embedder/implementations/random.py`. Returns random unit vectors
of configurable dimension. Used as the default when no real embedder is configured.

| Parameter | Default | Description |
|---|---|---|
| `dimension` | `768` | Dimensionality of the produced embeddings |

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
└── embedder/
    ├── __init__.py
    ├── base.py                       # Embedder ABC
    └── implementations/
        ├── __init__.py
        └── random.py                 # RandomEmbedder
tests/
└── libs/
    └── embedder/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_random.py
```

---

## Implementation Order

1. `Embedder` ABC
2. `RandomEmbedder`
3. Tests

---

## Acceptance Criteria

- [ ] `Embedder` ABC defined with: `dimension` property, `embed`, `embed_batch`
- [ ] `dimension` returns an integer representing the embedding dimensionality
- [ ] `embed` returns a `list[float]` of length `dimension`, never raises
- [ ] `embed_batch` returns a `list[list[float]]` with one embedding per input text
- [ ] `embed_batch` returns an empty list for empty input
- [ ] `RandomEmbedder` accepts `dimension` at construction time, defaults to `768`
- [ ] `RandomEmbedder.embed` returns a vector of the correct dimension
- [ ] `RandomEmbedder.embed_batch` returns correct number of embeddings
- [ ] `RandomEmbedder` embeddings are unit vectors
- [ ] Injected at construction time by the consuming project — no auto-instantiation
- [ ] Unit tests cover: `embed` returns correct dimension, `embed_batch` returns correct count, embeddings are unit vectors, `embed_batch` with empty input