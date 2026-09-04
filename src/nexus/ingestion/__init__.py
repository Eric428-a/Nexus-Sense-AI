"""
NEXUS-SENSE ingestion package.

The ingestion layer provides a common interface for collecting,
normalizing, and preparing information from heterogeneous sources.
"""

from .base import (
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceDocument,
    SourceType,
)
from .api_loader import APIDataLoader
from .csv_loader import CSVDataLoader
from .document_loader import DocumentLoader
from .event_stream import EventStreamLoader
from .web_loader import WebLoader

__all__ = [
    "APIDataLoader",
    "CSVDataLoader",
    "ContentChunk",
    "DocumentLoader",
    "EventStreamLoader",
    "IngestionRequest",
    "IngestionResult",
    "SourceDocument",
    "SourceType",
    "WebLoader",
]