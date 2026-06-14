[← README](../README.md)

# common/ — Shared Domain Models

## Principles

`common/` contains the shared domain models and enums used across the entire
codebase. It is the foundation that all other layers build upon. It has no
dependencies on any other layer in this codebase.

## Rules

- No imports from `libs/`, `backends/`, `pipelines/`
- No logic — only dataclasses and enums
- No default values that encode business decisions
- All layers may import from `common/`

## Contents

### `common/enums.py`

| Enum | Description |
|---|---|
| `FileType` | Supported MIME types |
| `Layout` | Page column layout |

### `common/models.py`

| Model | Description |
|---|---|
| `PageProfile` | Per-page structural metadata produced by the profiler |
| `DocumentProfile` | Document-level structural metadata |
| `ParsedPage` | Per-page extracted text content |
| `ParsedDocument` | Full parsed document with per-page content |
| `SourceReference` | Citation anchor — page range |
| `DocumentChunk` | Self-contained text fragment with source reference |
| `TreeNode` | Node in a `DocumentTree` |
| `DocumentTree` | Hierarchical document representation |
| `IndexedChunk` | A `DocumentChunk` paired with its embedding |

## Dependency Direction

```
common/ → (nothing)
```

Nothing in `common/` imports from anywhere else in this codebase.
Every other layer may import from `common/`.