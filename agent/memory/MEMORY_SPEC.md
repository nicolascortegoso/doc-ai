[← AGENT_SPEC](../AGENT_SPEC.md)

# Memory Module

## Overview

Provides a `Memory` ABC for conversational memory management. Injected into
agents at construction time. Agents do not hardcode any memory strategy.

`InMemoryMemory` ships as the only concrete implementation.

---

## Interface Contract

### `Memory` ABC

Defined in `agent/memory/base.py`.

| Method | Signature | Description |
|---|---|---|
| `add` | `(message: Message, session_id: UUID) -> None` | Add a message to the session history |
| `get` | `(session_id: UUID) -> list[Message]` | Retrieve all messages for a session. Returns empty list if not found |
| `clear` | `(session_id: UUID) -> None` | Clear all messages for a session. No-op if not found |

---

## `InMemoryMemory`

Defined in `agent/memory/implementations/memory.py`.

Stores messages in a Python dict keyed by `session_id`. Not thread-safe.
Suitable for testing and local development only.

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
└── memory/
    ├── __init__.py
    ├── base.py                       # Memory ABC
    └── implementations/
        ├── __init__.py
        └── memory.py                 # InMemoryMemory
tests/
└── test_agent/
    └── memory/
        └── implementations/
            └── test_memory.py
```

---

## Acceptance Criteria

- [ ] `Memory` ABC defined with: `add`, `get`, `clear`
- [ ] `get` returns empty list for unknown session
- [ ] `clear` is a no-op for unknown session
- [ ] `InMemoryMemory.add` appends message to session history
- [ ] `InMemoryMemory.get` returns messages in order added
- [ ] `InMemoryMemory.clear` removes all messages for a session
- [ ] Multiple sessions are isolated from each other
- [ ] Unit tests cover: add and get, get returns empty list for unknown session, clear removes messages, clear is no-op for unknown session, multiple sessions isolated