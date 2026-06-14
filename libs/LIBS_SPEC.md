[← README](../README.md)

# libs/ — Domain Logic Layer

## Principles

`libs/` contains pure domain logic. Every module is stateless, side-effect free,
and injectable. No module knows about databases, message queues, HTTP, or any
other infrastructure concern.

## Rules

- No imports from `backends/`, `pipelines/`
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

## External Dependencies

Only pure computation libraries are permitted — no I/O, no network, no storage.
All other external dependencies are injected, never hardcoded.

## Shared Models

All domain models live in `libs/common/`. No other `libs/` module defines
domain models.

## Module Specs

| Module | Spec |
|---|---|
| `profiler/` | [PROFILER_SPEC.md](profiler/PROFILER_SPEC.md) |
| `parser/` | [PARSER_SPEC.md](parser/PARSER_SPEC.md) |
| `chunker/` | [CHUNKER_SPEC.md](chunker/CHUNKER_SPEC.md) |
| `merger/` | [MERGER_SPEC.md](merger/MERGER_SPEC.md) |
| `indexer/` | [INDEXER_SPEC.md](indexer/INDEXER_SPEC.md) |