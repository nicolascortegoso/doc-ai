[← PROFILER_SPEC](../PROFILER_SPEC.md)

# Detector Module

## Overview

Provides a `Detector` ABC for MIME type detection and language detection. Injected
into profiler components at construction time. The profiler does not hardcode any
detection strategy.

`DefaultDetector` ships as the only concrete implementation.

---

## Interface Contract

### `Detector` ABC

Defined in `libs/profiler/detector/base.py`.

| Method | Signature | Description |
|---|---|---|
| `detect_mime` | `(file_bytes: bytes) -> FileType` | Returns a `FileType` resolved from magic bytes. Never raises. |
| `detect_language` | `(text: str) -> str` | Returns a locale code (e.g. `"en"`, `"fr"`). Never raises. |

---

## `DefaultDetector`

Defined in `libs/profiler/detector/implementations/default.py`.

- `detect_mime` — uses `python-magic` to resolve MIME type from magic bytes
- `detect_language` — always returns `"en"`

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| MIME detection | `python-magic` |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── profiler/
    └── detector/
        ├── __init__.py
        ├── base.py                       # Detector ABC
        └── implementations/
            ├── __init__.py
            └── default.py               # DefaultDetector
tests/
└── test_libs/
    └── profiler/
        └── detector/
            └── implementations/
                └── test_default.py
```

---

## Acceptance Criteria

- [ ] `Detector` ABC defined with: `detect_mime`, `detect_language`
- [ ] `detect_mime` returns a `FileType`, never raises
- [ ] `detect_language` returns a locale code string, never raises
- [ ] `DefaultDetector.detect_mime` uses `python-magic`
- [ ] `DefaultDetector.detect_language` always returns `"en"`
- [ ] Unit tests cover: `detect_mime` returns correct `FileType`, `detect_language` returns `"en"`, neither raises