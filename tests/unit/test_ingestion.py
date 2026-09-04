import json

import pytest

from src.nexus.ingestion.api_loader import APIDataLoader
from src.nexus.ingestion.base import (
    ContentChunk,
    IngestionRequest,
    SourceDocument,
    SourceType,
)
from src.nexus.ingestion.csv_loader import CSVDataLoader
from src.nexus.ingestion.document_loader import DocumentLoader
from src.nexus.ingestion.event_stream import EventStreamLoader


def test_source_document_generates_checksum() -> None:
    document = SourceDocument(
        source_type=SourceType.DOCUMENT,
        content="NEXUS-SENSE intelligence.",
    )

    assert document.checksum
    assert len(document.checksum) == 64


def test_content_chunk_generates_fingerprint() -> None:
    chunk = ContentChunk(
        source_id="src_001",
        content="Example content.",
    )

    assert chunk.fingerprint
    assert len(chunk.fingerprint) == 64


@pytest.mark.asyncio
async def test_document_loader_from_content() -> None:
    loader = DocumentLoader(
        chunk_size=20,
        chunk_overlap=5,
    )

    request = IngestionRequest(
        source_type=SourceType.DOCUMENT,
        content=(
            "NEXUS-SENSE is an agentic intelligence platform "
            "designed for complex data processing."
        ),
        title="Example Document",
    )

    result = await loader.load(request)

    assert result.success is True
    assert len(result.documents) == 1
    assert len(result.chunks) > 1


@pytest.mark.asyncio
async def test_csv_loader() -> None:
    loader = CSVDataLoader()

    request = IngestionRequest(
        source_type=SourceType.CSV,
        content=(
            "name,type\n"
            "Alpha,organization\n"
            "Beta,organization\n"
        ),
    )

    result = await loader.load(request)

    assert result.success is True
    assert result.metadata["row_count"] == 2
    assert len(result.chunks) == 2


@pytest.mark.asyncio
async def test_event_stream_loader() -> None:
    loader = EventStreamLoader()

    payload = {
        "event_type": "signal_detected",
        "payload": {
            "signal": "example",
        },
    }

    request = IngestionRequest(
        source_type=SourceType.EVENT_STREAM,
        content=json.dumps(payload),
    )

    result = await loader.load(request)

    assert result.success is True
    assert result.metadata["event_type"] == "signal_detected"
    assert len(result.documents) == 1


def test_invalid_chunk_configuration() -> None:
    with pytest.raises(ValueError):
        DocumentLoader(
            chunk_size=100,
            chunk_overlap=100,
        )


def test_document_can_add_tags() -> None:
    document = SourceDocument(
        source_type=SourceType.MANUAL,
        content="Example",
    )

    document.add_tag("research")
    document.add_tag("research")

    assert document.tags == ["research"]