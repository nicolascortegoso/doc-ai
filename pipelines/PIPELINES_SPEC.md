[← README](../README.md)

# pipelines/ — Orchestration Layer

## Principles

`pipelines/` contains orchestration abstractions. Every module defines an ABC
for a specific pipeline concern. Concrete implementations (Celery, synchronous,
etc.) live in the infrastructure layer.

## Rules

- No imports from the infrastructure layer or any framework
- May import from `libs/` and `backends/`
- May import from `common/`
- Defines stage contracts, not execution strategies
- Every pipeline is fully resumable via `IngestionStatus`

## Pattern

```
pipelines/<pipeline>/
    base.py              # Pipeline ABC
    serializers.py       # Pipeline output serialisers (where needed)
    models.py            # Pipeline-specific models (where needed)
```

## Dependency Direction

```
pipelines/ → common/ + libs/ + backends/
```

## Testing Convention

Test directories are prefixed with `test_` to avoid shadowing top-level package names:

```
tests/
└── test_pipelines/
    └── ingestion/
        ├── test_base.py
        └── test_serializers.py
```

## Pipeline Specs

| Pipeline | Spec |
|---|---|
| `ingestion/` | [INGESTION_PIPELINE_SPEC.md](ingestion/INGESTION_PIPELINE_SPEC.md) |
| `inference/` | _(coming soon)_ |