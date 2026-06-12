from .base import LanguageDetector
from .implementations.dummy import DummyLanguageDetector

__all__ = [
    "DummyLanguageDetector",
    "LanguageDetector",
]
