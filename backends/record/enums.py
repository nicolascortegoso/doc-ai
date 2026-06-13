from enum import Enum


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROFILING = "profiling"
    PROFILED = "profiled"
    PARSING = "parsing"
    PARSED = "parsed"
    CHUNKING = "chunking"
    CHUNKED = "chunked"
    MERGING = "merging"
    MERGED = "merged"
    EMBEDDING = "embedding"
    EMBEDDED = "embedded"
    INDEXED = "indexed"
    FAILED = "failed"