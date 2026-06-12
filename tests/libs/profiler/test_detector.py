import struct
import zlib

import pytest

from libs.profiler.detector import MimeTypeDetector
from libs.common.enums import FileType


class TestMimeTypeDetector:
    def setup_method(self):
        self.detector = MimeTypeDetector()

    def test_detects_pdf(self, pdf_bytes):
        assert self.detector.detect(pdf_bytes) == FileType.PDF

    def test_detects_png(self, png_bytes):
        assert self.detector.detect(png_bytes) == FileType.PNG

    def test_returns_unknown_for_random_bytes(self):
        result = self.detector.detect(b"\x00\x01\x02\x03garbage")
        assert result == FileType.UNKNOWN

    def test_returns_unknown_for_empty_bytes(self):
        result = self.detector.detect(b"")
        assert result == FileType.UNKNOWN

    def test_never_raises(self):
        # Should not raise for any input
        result = self.detector.detect(b"definitely not a real file")
        assert isinstance(result, FileType)


# ---------------------------------------------------------------------------
# Fixtures — minimal valid magic-byte headers
# ---------------------------------------------------------------------------

@pytest.fixture
def pdf_bytes() -> bytes:
    # Minimal PDF magic bytes
    return b"%PDF-1.4\n%%EOF"


@pytest.fixture
def png_bytes() -> bytes:
    """Minimal valid PNG (1x1 white pixel) — enough for libmagic to identify."""
    def _chunk(type_: bytes, data: bytes) -> bytes:
        payload = type_ + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = _chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
    iend = _chunk(b"IEND", b"")
    return sig + ihdr + idat + iend
