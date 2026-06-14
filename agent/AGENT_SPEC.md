[← README](../README.md)

# agent/ — Conversational Agent Layer

## Overview

Provides abstractions for conversational AI agents. An agent processes user
messages, reasons about them, invokes tools, and returns a response — all
within a session context maintained by an injected `Memory`.

Designed to accommodate both simple QA systems and complex multi-turn reasoning
agents. The difference lies entirely in the implementation, not the contract.

No concrete `Agent` implementation ships with this module. Implementations
live in the infrastructure layer.

---

## Principles

- No imports from `pipelines/`
- May import from `common/`, `libs/`, `backends/`
- `Agent` is stateless — session state is owned by `Memory`
- Every abstraction ships a default no-op implementation
- Fully testable without any external service

---

## Data Models

### `Message` Dataclass

Defined in `common/models.py`.

| Field | Type | Description |
|---|---|---|
| `role` | `str` | The role of the message sender (e.g. `"user"`, `"assistant"`, `"tool"`) |
| `content` | `str` | The message content |

### `AgentResponse` Dataclass

Defined in `common/models.py`.

| Field | Type | Description |
|---|---|---|
| `message` | `str` | The agent's response |
| `sources` | `list[DocumentChunk]` | Chunks used to generate the response |
| `reasoning` | `str` | The agent's reasoning process |
| `session_id` | `UUID` | The session this response belongs to |

---

## Interface Contract

### `Agent` ABC

Defined in `agent/base.py`.

| Method | Signature | Description |
|---|---|---|
| `chat` | `(message: str, session_id: UUID) -> AgentResponse` | Process a message and return a response. Never raises. |

---

## Injected Dependencies

| Dependency | Spec |
|---|---|
| `Memory` | [MEMORY_SPEC.md](memory/MEMORY_SPEC.md) |
| `Tool` list | [TOOL_SPEC.md](tool/TOOL_SPEC.md) |

---

## Dependency Direction

```
agent/ → common/ + libs/ + backends/
```

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
agent/
├── __init__.py
├── base.py                           # Agent ABC
├── memory/
│   ├── __init__.py
│   ├── base.py                       # Memory ABC
│   └── implementations/
│       ├── __init__.py
│       └── memory.py                 # InMemoryMemory
└── tool/
    ├── __init__.py
    ├── base.py                       # Tool ABC
    └── implementations/
        ├── __init__.py
        └── default.py               # DefaultTool
tests/
└── test_agent/
    ├── __init__.py
    ├── memory/
    │   └── implementations/
    │       └── test_memory.py
    └── tool/
        └── implementations/
            └── test_default.py
```

---

## Implementation Order

1. `Message` + `AgentResponse` dataclasses in `common/models.py`
2. `Tool` ABC + `DefaultTool`
3. `Memory` ABC + `InMemoryMemory`
4. `Agent` ABC
5. Tests

---

## Acceptance Criteria

- [ ] `Message` dataclass defined in `common/models.py` with: `role`, `content`
- [ ] `AgentResponse` dataclass defined in `common/models.py` with: `message`, `sources`, `reasoning`, `session_id`
- [ ] `Agent` ABC defined with single abstract method `chat(message: str, session_id: UUID) -> AgentResponse`
- [ ] `chat` never raises
- [ ] `Memory` injected at construction time
- [ ] `Tool` list injected at construction time
- [ ] Unit tests cover: `Tool` and `Memory` default implementations