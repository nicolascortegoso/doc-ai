# libs/ — Domain Logic Layer

[← README](../README.md)

## Principles

`libs/` contains pure domain logic. Every module is stateless, side-effect free,
and injectable. No module knows about databases, message queues, HTTP, or any
other infrastructure concern.

## Rules

- No imports from `backends/`, `pipelines/`, or `app/`
- No network calls, no file system writes, no global state
- All external dependencies injected at construction time
- Every module ships a default no-op implementation
- Every module is fully testable without any external service

## Pattern

Every module follows the same structure:

```
libs/<module>/
    base.py              # ABC
    registry.py          # Priority-based dispatch (where applicable)
    implementations/
        default.py       # Default implementation
```

## Permitted External Dependencies

- `pymupdf` — PDF parsing
- `python-magic` — MIME type detection

All other external dependencies are injected, never hardcoded.

## Shared Models

All domain models live in `libs/common/`. No other `libs/` module defines
domain models.

## Module Specs

| Module | Spec |
|---|---|
| `common/` | — |
| `detector/` | [DETECTOR_SPEC.md](DETECTOR_SPEC.md) |
| `profiler/` | [PROFILER_SPEC.md](PROFILER_SPEC.md) |
| `postprocessor/` | [POSTPROCESSOR_SPEC.md](POSTPROCESSOR_SPEC.md) |
| `parser/` | [PARSER_SPEC.md](PARSER_SPEC.md) |
| `splitter/` | [SPLITTER_SPEC.md](SPLITTER_SPEC.md) |
| `chunker/` | [CHUNKER_SPEC.md](CHUNKER_SPEC.md) |
| `reducer/` | [REDUCER_SPEC.md](REDUCER_SPEC.md) |
| `merger/` | [MERGER_SPEC.md](MERGER_SPEC.md) |
| `embedder/` | [EMBEDDER_SPEC.md](EMBEDDER_SPEC.md) |
| `indexer/` | [INDEXER_SPEC.md](INDEXER_SPEC.md) |