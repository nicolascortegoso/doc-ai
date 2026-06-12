from enum import Enum


class FileType(str, Enum):
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PPT = "application/vnd.ms-powerpoint"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    XLS = "application/vnd.ms-excel"
    CSV = "text/csv"
    TXT = "text/plain"
    HTML = "text/html"
    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    UNKNOWN = "application/octet-stream"


class Layout(str, Enum):
    SINGLE_COLUMN = "single_column"
    MULTI_COLUMN = "multi_column"
    MIXED = "mixed"
    UNKNOWN = "unknown"
