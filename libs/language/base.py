from abc import ABC, abstractmethod


class LanguageDetector(ABC):
    @abstractmethod
    def detect(self, text: str) -> str:
        """Detect the language of the given text.

        Returns a locale code (e.g. "en", "fr"). Never raises.
        """
