# Document-AI

Document-AI is a modular, production-grade platform for intelligent document ingestion, semantic search, and retrieval-augmented generation (RAG). It enables organizations to transform unstructured documents into a queryable knowledge base, supporting natural language search, citation-grounded answers, and fine-grained access control.

The platform is built around clean abstractions and swappable backends — identity providers, storage, databases, task queues, and document sources are all configurable without code changes.

## Architecture

The codebase is organised into the following layers:

- [`libs/`](libs/LIB_SPEC.md) — pure domain logic, stateless and injectable
- [`backends/`](backends/BACKEND_SPEC.md) — storage abstractions
- [`pipelines/`](pipelines/PIPELINE_SPEC.md) — orchestration layer