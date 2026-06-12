import magic

from libs.common.enums import FileType


class MimeTypeDetector:
    """Magic-byte MIME detection.

    Returns a FileType for recognised signatures.
    Returns FileType.UNKNOWN for unrecognised signatures — never raises.
    """

    _MIME_TO_FILE_TYPE: dict[str, FileType] = {ft.value: ft for ft in FileType if ft is not FileType.UNKNOWN}

    def detect(self, file_bytes: bytes) -> FileType:
        try:
            mime_str = magic.from_buffer(file_bytes, mime=True)
            return self._MIME_TO_FILE_TYPE.get(mime_str, FileType.UNKNOWN)
        except Exception:
            return FileType.UNKNOWN
