import pytest


@pytest.fixture
def pdf_bytes() -> bytes:
    """Minimal valid PDF magic bytes — enough for MIME detection."""
    return b"%PDF-1.4 minimal test content"


@pytest.fixture
def png_bytes() -> bytes:
    """Minimal valid PNG — signature + IHDR chunk, enough for libmagic."""
    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"
    # IHDR chunk: length(4) + type(4) + width(4) + height(4) + bit_depth(1)
    # + color_type(1) + compression(1) + filter(1) + interlace(1) + CRC(4)
    ihdr = (
        b"\x00\x00\x00\x0d"  # chunk length = 13
        b"IHDR"
        b"\x00\x00\x00\x01"  # width = 1
        b"\x00\x00\x00\x01"  # height = 1
        b"\x08\x02"          # bit depth = 8, colour type = 2 (RGB)
        b"\x00\x00\x00"      # compression, filter, interlace
        b"\x90\x77\x53\xde"  # CRC (not validated by libmagic)
    )
    return sig + ihdr
