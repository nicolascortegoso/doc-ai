[← AGENT_SPEC](../AGENT_SPEC.md)

# Tool Module

## Overview

Provides a `Tool` ABC for agent capabilities. Tools are injected into agents
as a list at construction time. The agent decides which tools to invoke during
the reasoning cycle based on each tool's `name` and `description`.

`DefaultTool` ships as the only concrete implementation — a no-op used for
testing.

---

## Interface Contract

### `Tool` ABC

Defined in `agent/tool/base.py`.

| Attribute/Method | Type | Description |
|---|---|---|
| `name` | `str` (property) | Unique name identifying the tool |
| `description` | `str` (property) | Human-readable description — used by the agent to decide when to invoke it |
| `invoke` | `(input: str) -> str` | Execute the tool with the given input. Never raises. |

---

## `DefaultTool`

Defined in `agent/tool/implementations/default.py`.

Returns an empty string. Used as a no-op placeholder for testing.

| Attribute | Value |
|---|---|
| `name` | `"default"` |
| `description` | `"A no-op tool that returns an empty string."` |

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
└── tool/
    ├── __init__.py
    ├── base.py                       # Tool ABC
    └── implementations/
        ├── __init__.py
        └── default.py               # DefaultTool
tests/
└── test_agent/
    └── tool/
        └── implementations/
            └── test_default.py
```

---

## Acceptance Criteria

- [ ] `Tool` ABC defined with: `name` property, `description` property, `invoke` method
- [ ] `invoke` never raises
- [ ] `DefaultTool.name` returns `"default"`
- [ ] `DefaultTool.description` returns a non-empty string
- [ ] `DefaultTool.invoke` returns empty string
- [ ] Unit tests cover: `invoke` returns empty string, never raises, name and description are strings