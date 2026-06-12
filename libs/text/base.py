from abc import ABC, abstractmethod


class TextCleaner(ABC):
    @abstractmethod
    def clean(self, text: str) -> str:
        """Clean and normalise the given text.

        Returns the cleaned string. Never raises.
        """