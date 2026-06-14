from abc import ABC, abstractmethod

from common.enums import FileType


class Detector(ABC):
    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Detect the language of the given text.

        Returns a locale code (e.g. "en", "fr"). Never raises.
        """

    @abstractmethod
    def detect_mime(self, file_bytes: bytes) -> FileType:
        """Detect the MIME type of the given file bytes.

        Returns a FileType resolved from magic bytes.
        Returns FileType.UNKNOWN for unrecognised signatures. Never raises.
        """