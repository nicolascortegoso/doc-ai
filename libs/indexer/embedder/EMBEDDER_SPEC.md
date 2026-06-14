[← INDEXER_SPEC](../INDEXER_SPEC.md)

# Embedder Module

## Overview

Provides an `Embedder` ABC for text-to-vector transformation. Injected into indexing
strategies at construction time. Strategies do not hardcode any embedding logic.

`RandomEmbedder` ships as the only concrete implementation.

---

## Interface Contract

### `Embedder` ABC

Defined in `libs/indexer/embedder/base.py`.

| Method/Property | Signature | Description |
|---|---|---|
| `dimension` | `int` (property) | The dimensionality of the produced embeddings |
| `embed` | `(text: str) -> list[float]` | Embed a single text. Never raises. |
| `embed_batch` | `(texts: list[str]) -> list[list[float]]` | Embed multiple texts. Returns one embedding per input text. Never raises. |

---

## `RandomEmbedder`

Defined in `libs/indexer/embedder/implementations/random.py`.

Returns random unit vectors of configurable dimension. Used as the default when
no real embedder is configured.

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
└── indexer/
    └── embedder/
        ├── __init__.py
        ├── base.py                       # Embedder ABC
        └── implementations/
            ├── __init__.py
            └── random.py                 # RandomEmbedder
tests/
└── test_libs/
    └── indexer/
        └── embedder/
            └── implementations/
                └── test_random.py
```

---

## Acceptance Criteria

- [ ] `Embedder` ABC defined with: `dimension` property, `embed`, `embed_batch`
- [ ] `dimension` returns an integer representing the embedding dimensionality
- [ ] `embed` returns a `list[float]` of length `dimension`, never raises
- [ ] `embed_batch` returns a `list[list[float]]` with one embedding per input text
- [ ] `embed_batch` returns an empty list for empty input
- [ ] `RandomEmbedder` accepts `dimension` at construction time, defaults to `768`
- [ ] `RandomEmbedder` embeddings are unit vectors
- [ ] Unit tests cover: `embed` returns correct dimension, `embed_batch` returns correct count, embeddings are unit vectors, `embed_batch` with empty input