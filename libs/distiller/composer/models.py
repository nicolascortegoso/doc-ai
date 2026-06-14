from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ComposerInput:
    content: str
    instruction: str
    context: dict | None = None