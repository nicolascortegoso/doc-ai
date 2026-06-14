from __future__ import annotations

import json
import re
from typing import ClassVar
from uuid import UUID

from common.enums import FileType
from common.models import GlossaryEntry, ParsedDocument
from libs.distiller.analyzer.base import Analyzer
from libs.distiller.analyzer.implementations.default import DefaultAnalyzer
from libs.distiller.analyzer.models import AnalyzerInput
from libs.distiller.base import BaseDistillerStrategy
from libs.distiller.composer.base import Composer
from libs.distiller.composer.implementations.default import DefaultComposer
from libs.distiller.composer.models import ComposerInput


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


class GlossaryDistillerStrategy(BaseDistillerStrategy):
    """Extracts glossary entries from a ParsedDocument.

    For each page, calls the Analyzer to extract terms and definitions,
    then calls the Composer to refine each entry into a well-formed definition.

    Args:
        analyzer: Injected Analyzer (NLU). Default: DefaultAnalyzer.
        composer: Injected Composer (NLG). Default: DefaultComposer.
    """

    supported_mime_types: ClassVar[list[FileType]] = list(FileType)

    EXTRACT_INSTRUCTION = (
        "Extract all domain-specific terms and their definitions from the text. "
        "Return a JSON object with a 'terms' list. Each item must have: "
        "'term' (string), 'definition' (string), 'evidence' (verbatim excerpt). "
        "Return only JSON, no preamble."
    )

    COMPOSE_INSTRUCTION = (
        "Refine the following extracted definition into a clear, concise, "
        "well-formed sentence. Return only the refined definition text."
    )

    def __init__(
        self,
        analyzer: Analyzer = None,
        composer: Composer = None,
    ) -> None:
        self._analyzer = analyzer or DefaultAnalyzer()
        self._composer = composer or DefaultComposer()

    def can_handle(self, document: ParsedDocument) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def distill(
        self, document: ParsedDocument, document_id: UUID
    ) -> list[GlossaryEntry]:
        entries = []

        for page in document.pages:
            if not page.content.strip():
                continue

            raw = self._analyzer.analyze(AnalyzerInput(
                content=page.content,
                instruction=self.EXTRACT_INSTRUCTION,
            ))

            terms = self._parse_terms(raw)

            for term_data in terms:
                term = term_data.get("term", "").strip()
                definition = term_data.get("definition", "").strip()
                evidence = term_data.get("evidence", "").strip()

                if not term or not definition:
                    continue

                refined = self._composer.compose(ComposerInput(
                    content=definition,
                    instruction=self.COMPOSE_INSTRUCTION,
                ))

                entries.append(GlossaryEntry(
                    term=term,
                    slug=_slugify(term),
                    definition=refined or definition,
                    evidence=evidence,
                    document_id=document_id,
                ))

        return entries

    def _parse_terms(self, raw: str) -> list[dict]:
        try:
            data = json.loads(raw)
            if isinstance(data.get("terms"), list):
                return data["terms"]
        except (json.JSONDecodeError, AttributeError):
            pass
        return []