"""Immutable synthetic evidence corpus for deterministic local retrieval."""

import hashlib
from typing import Annotated, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
)
from incident_diagnostic_api.retrieval.models import (
    EvidenceChunk,
    EvidenceDocument,
    EvidenceSource,
)

Sources = Annotated[
    tuple[EvidenceSource, ...],
    Field(min_length=1, max_length=20),
]
Documents = Annotated[
    tuple[EvidenceDocument, ...],
    Field(min_length=1, max_length=100),
]
Chunks = Annotated[
    tuple[EvidenceChunk, ...],
    Field(min_length=1, max_length=1_000),
]


def calculate_content_hash(content: str) -> ContentHash:
    """Return the deterministic SHA-256 hash for UTF-8 content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class SyntheticEvidenceCorpus(ContractModel):
    """Bounded, immutable, internally consistent synthetic evidence."""

    corpus_id: OpaqueIdentifier
    corpus_version: OpaqueIdentifier
    sources: Sources
    documents: Documents
    chunks: Chunks

    @model_validator(mode="after")
    def validate_corpus_integrity(self) -> Self:
        """Validate uniqueness, lineage, metadata, and content integrity."""

        sources_by_id: dict[str, EvidenceSource] = {}
        documents_by_id: dict[str, EvidenceDocument] = {}
        chunk_ids: set[str] = set()

        for source in self.sources:
            if source.source_id in sources_by_id:
                raise ValueError("source identifiers must be unique")

            sources_by_id[source.source_id] = source

        for document in self.documents:
            if document.document_id in documents_by_id:
                raise ValueError("document identifiers must be unique")

            resolved_source = sources_by_id.get(document.source_id)

            if resolved_source is None:
                raise ValueError("every document must reference a corpus source")

            if document.source_kind is not resolved_source.source_kind:
                raise ValueError("document source kind must match its source")

            if document.tenant_id != resolved_source.tenant_id:
                raise ValueError("document tenant must match its source tenant")

            if not set(document.service_ids).issubset(resolved_source.service_ids):
                raise ValueError("document services must be allowed by its source")

            if document.sensitivity is not resolved_source.sensitivity:
                raise ValueError("document sensitivity must match its source")

            if calculate_content_hash(document.content) != document.content_hash:
                raise ValueError("document content hash is invalid")

            documents_by_id[document.document_id] = document

        for chunk in self.chunks:
            if chunk.chunk_id in chunk_ids:
                raise ValueError("chunk identifiers must be unique")

            chunk_ids.add(chunk.chunk_id)
            resolved_document = documents_by_id.get(chunk.document_id)

            if resolved_document is None:
                raise ValueError("every chunk must reference a corpus document")

            if chunk.document_version != resolved_document.document_version:
                raise ValueError("chunk document version must match its document")

            if chunk.source_id != resolved_document.source_id:
                raise ValueError("chunk source must match its document source")

            if chunk.source_kind is not resolved_document.source_kind:
                raise ValueError("chunk source kind must match its document")

            if chunk.tenant_id != resolved_document.tenant_id:
                raise ValueError("chunk tenant must match its document tenant")

            if chunk.service_ids != resolved_document.service_ids:
                raise ValueError("chunk services must match its document services")

            if chunk.sensitivity is not resolved_document.sensitivity:
                raise ValueError("chunk sensitivity must match its document")

            if chunk.lifecycle_status is not resolved_document.lifecycle_status:
                raise ValueError("chunk lifecycle must match its document lifecycle")

            if calculate_content_hash(chunk.content) != chunk.content_hash:
                raise ValueError("chunk content hash is invalid")

        return self
