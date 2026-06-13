import magic

from libs.common.enums import FileType
from libs.detector.base import Detector


class DefaultDetector(Detector):
    """Default detector implementation.

    detect_language: Always returns "en".
    detect_mime: Magic-byte inspection via python-magic. Returns
        FileType.UNKNOWN for unrecognised signatures — never raises.
    """

    _MIME_TO_FILE_TYPE: dict[str, FileType] = {
        ft.value: ft for ft in FileType if ft is not FileType.UNKNOWN
    }

    def detect_language(self, text: str) -> str:
        return "en"

    def detect_mime(self, file_bytes: bytes) -> FileType:
        try:
            mime_str = magic.from_buffer(file_bytes, mime=True)
            return self._MIME_TO_FILE_TYPE.get(mime_str, FileType.UNKNOWN)
        except Exception:
            return FileType.UNKNOWN