from __future__ import annotations

import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from common.enums import FileType
from common.models import GlossaryEntry, ParsedDocument, ParsedPage
from libs.distiller.analyzer.base import Analyzer
from libs.distiller.composer.base import Composer
from libs.distiller.implementations.glossary import GlossaryDistillerStrategy


def _make_document(pages: list[tuple[int, str]]) -> ParsedDocument:
    return ParsedDocument(
        mime_type=FileType.PDF,
        page_count=len(pages),
        pages=[
            ParsedPage(page_number=n, content=content, strategy="PlainPdfExtractionStrategy")
            for n, content in pages
        ],
    )


def _make_analyzer_response(terms: list[dict]) -> str:
    return json.dumps({"terms": terms})


class TestGlossaryDistillerMetadata:
    def test_supported_mime_types_covers_all(self):
        strategy = GlossaryDistillerStrategy()
        for ft in FileType:
            assert ft in strategy.supported_mime_types

    def test_get_priority_returns_1(self):
        assert GlossaryDistillerStrategy().get_priority() == 1

    def test_can_handle_always_returns_true(self):
        strategy = GlossaryDistillerStrategy()
        assert strategy.can_handle(_make_document([(1, "content")])) is True


class TestGlossaryDistillerDistill:
    def test_empty_document_returns_empty_list(self):
        strategy = GlossaryDistillerStrategy()
        doc = ParsedDocument(mime_type=FileType.PDF, page_count=0, pages=[])
        assert strategy.distill(doc, uuid4()) == []

    def test_empty_page_content_skipped(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer)
        doc = _make_document([(1, "   ")])
        result = strategy.distill(doc, uuid4())
        assert result == []
        mock_analyzer.analyze.assert_not_called()

    def test_analyzer_called_per_page(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = json.dumps({"terms": []})
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer)
        doc = _make_document([(1, "page one"), (2, "page two")])
        strategy.distill(doc, uuid4())
        assert mock_analyzer.analyze.call_count == 2

    def test_returns_glossary_entries(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "Application Programming Interface", "evidence": "An API is..."},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "A refined definition."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert len(result) == 1
        assert isinstance(result[0], GlossaryEntry)

    def test_entry_has_correct_term(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "A programming interface", "evidence": "An API is..."},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Refined."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result[0].term == "API"

    def test_entry_has_correct_slug(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "REST API", "definition": "A web API", "evidence": "REST API is..."},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Refined."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result[0].slug == "rest-api"

    def test_entry_document_id_stamped(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "A programming interface", "evidence": "An API is..."},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Refined."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        doc_id = uuid4()
        result = strategy.distill(_make_document([(1, "content")]), doc_id)
        assert result[0].document_id == doc_id

    def test_composer_called_per_term(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "def1", "evidence": "ev1"},
            {"term": "SDK", "definition": "def2", "evidence": "ev2"},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Refined."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        strategy.distill(_make_document([(1, "content")]), uuid4())
        assert mock_composer.compose.call_count == 2

    def test_composer_output_used_as_definition(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "raw def", "evidence": "ev"},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Composed definition."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result[0].definition == "Composed definition."

    def test_falls_back_to_raw_definition_when_composer_returns_empty(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "API", "definition": "raw def", "evidence": "ev"},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = ""
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result[0].definition == "raw def"

    def test_skips_terms_without_term_or_definition(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = _make_analyzer_response([
            {"term": "", "definition": "some def", "evidence": "ev"},
            {"term": "API", "definition": "", "evidence": "ev"},
        ])
        mock_composer = MagicMock(spec=Composer)
        mock_composer.compose.return_value = "Refined."
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer, composer=mock_composer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result == []

    def test_invalid_analyzer_output_returns_empty(self):
        mock_analyzer = MagicMock(spec=Analyzer)
        mock_analyzer.analyze.return_value = "not valid json"
        strategy = GlossaryDistillerStrategy(analyzer=mock_analyzer)
        result = strategy.distill(_make_document([(1, "content")]), uuid4())
        assert result == []