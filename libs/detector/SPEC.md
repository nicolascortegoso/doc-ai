# Detector Module

## Overview

Provides a unified `Detector` ABC for document-level detection concerns — currently
language detection and MIME type detection. Designed for dependency injection so that
consuming modules remain decoupled from any specific detection implementation.

`DefaultDetector` ships as the only concrete implementation.

---

## Interface Contract

### `Detector` ABC

Defined in `libs/detector/base.py`.

| Method | Signature | Description |
|---|---|---|
| `detect_language` | `(text: str) -> str` | Returns a locale code (e.g. `"en"`, `"fr"`). Never raises. |
| `detect_mime` | `(file_bytes: bytes) -> FileType` | Returns a `FileType` resolved from magic bytes. Returns `FileType.UNKNOWN` for unrecognised signatures. Never raises. |

Both methods are abstract — every implementation must explicitly declare them.

---

## `DefaultDetector`

Defined in `libs/detector/implementations/default.py`.

| Method | Behaviour |
|---|---|
| `detect_language` | Always returns `"en"`. |
| `detect_mime` | Magic-byte inspection via `python-magic`. Returns `FileType.UNKNOWN` for unrecognised signatures — never raises. |

---

## Tech Stack

| Decision | Choice |
|---|---|
| Python | 3.12 |
| MIME detection | `python-magic` + `libmagic` system dependency |
| Language detection | Always returns `"en"` in `DefaultDetector` |
| Testing | `pytest` + `pytest-cov` |
| Linting / formatting | `ruff` |

---

## Folder Structure

```
libs/
└── detector/
    ├── __init__.py
    ├── base.py                       # Detector ABC
    └── implementations/
        ├── __init__.py
        └── default.py                # DefaultDetector
tests/
└── libs/
    └── detector/
        ├── __init__.py
        └── implementations/
            ├── __init__.py
            └── test_default.py
```

---

## Implementation Order

1. `Detector` ABC
2. `DefaultDetector`
3. Tests

---

## Acceptance Criteria

- [ ] `Detector` ABC defined with two abstract methods: `detect_language` and `detect_mime`
- [ ] `detect_language(text: str) -> str` — returns a locale code, never raises
- [ ] `detect_mime(file_bytes: bytes) -> FileType` — returns a `FileType`, never raises
- [ ] `DefaultDetector` implements both methods
- [ ] `DefaultDetector.detect_language` always returns `"en"`
- [ ] `DefaultDetector.detect_mime` uses `python-magic` for magic-byte inspection
- [ ] `DefaultDetector.detect_mime` returns `FileType.UNKNOWN` for unrecognised signatures
- [ ] `DefaultDetector.detect_mime` never raises
- [ ] `DefaultDetector.detect_language` never raises
- [ ] Injected at construction time by the consuming project — no auto-instantiation
- [ ] Unit tests cover: `detect_language` always returns `"en"`, `detect_mime` correct detection, `detect_mime` returns `FileType.UNKNOWN` fallback, `detect_mime` never raises