import struct
import zlib

import pytest

from common.enums import FileType
from libs.profiler.detector.implementations.default import DefaultDetector


@pytest.fixture
def detector() -> DefaultDetector:
    return DefaultDetector()


@pytest.fixture
def pdf_bytes() -> bytes:
    return b"%PDF-1.4\n%%EOF"


@pytest.fixture
def png_bytes() -> bytes:
    def _chunk(type_: bytes, data: bytes) -> bytes:
        payload = type_ + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = _chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
    iend = _chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


class TestDefaultDetectorLanguage:
    def test_returns_en_for_any_text(self, detector):
        assert detector.detect_language("Hello, world!") == "en"

    def test_returns_en_for_non_english_text(self, detector):
        assert detector.detect_language("Bonjour le monde") == "en"

    def test_returns_en_for_empty_string(self, detector):
        assert detector.detect_language("") == "en"

    def test_never_raises(self, detector):
        result = detector.detect_language("こんにちは")
        assert result == "en"


class TestDefaultDetectorMime:
    def test_detects_pdf(self, detector, pdf_bytes):
        assert detector.detect_mime(pdf_bytes) == FileType.PDF

    def test_detects_png(self, detector, png_bytes):
        assert detector.detect_mime(png_bytes) == FileType.PNG

    def test_returns_unknown_for_random_bytes(self, detector):
        assert detector.detect_mime(b"\x00\x01\x02\x03garbage") == FileType.UNKNOWN

    def test_returns_unknown_for_empty_bytes(self, detector):
        assert detector.detect_mime(b"") == FileType.UNKNOWN

    def test_never_raises(self, detector):
        result = detector.detect_mime(b"definitely not a real file")
        assert isinstance(result, FileType)