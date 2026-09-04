"""
CSV ingestion loader.
"""

import csv
import io
from time import perf_counter

from .base import (
    BaseLoader,
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceType,
)


class CSVDataLoader(BaseLoader):
    """
    Loader for CSV data.

    Rows are normalized into textual representations so they can
    participate in downstream retrieval and reasoning.
    """

    source_type = SourceType.CSV

    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Load CSV content."""
        started = perf_counter()

        try:
            content = await self._read_content(request)

            delimiter = request.options.get(
                "delimiter",
                ",",
            )

            reader = csv.DictReader(
                io.StringIO(content),
                delimiter=delimiter,
            )

            rows = list(reader)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV input does not contain a header row."
                )

            normalized_rows = [
                self._normalize_row(row)
                for row in rows
            ]

            normalized_content = "\n".join(
                normalized_rows
            )

            document = self.create_document(
                content=normalized_content,
                title=request.title or "CSV Dataset",
                uri=request.uri,
                mime_type="text/csv",
                metadata={
                    **request.metadata,
                    "columns": reader.fieldnames,
                    "row_count": len(rows),
                },
            )

            chunks = [
                ContentChunk(
                    source_id=document.id,
                    content=row,
                    index=index,
                    metadata={
                        "row_index": index,
                        "source_format": "csv",
                    },
                )
                for index, row in enumerate(normalized_rows)
            ]

            for chunk in chunks:
                document.add_chunk(chunk)

            elapsed_ms = (perf_counter() - started) * 1000

            return IngestionResult(
                request_id=request.id,
                success=True,
                documents=[document],
                chunks=chunks,
                processing_time_ms=elapsed_ms,
                metadata={
                    "columns": reader.fieldnames,
                    "row_count": len(rows),
                },
            )

        except (OSError, ValueError, csv.Error) as exc:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[f"CSV ingestion failed: {exc}"],
            )

    @staticmethod
    async def _read_content(
        request: IngestionRequest,
    ) -> str:
        """Read CSV from inline content or local file."""
        if request.content is not None:
            return request.content

        if not request.uri:
            raise ValueError(
                "CSV ingestion requires content or uri."
            )

        with open(
            request.uri,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:
            return file.read()

    @staticmethod
    def _normalize_row(
        row: dict[str, str | None],
    ) -> str:
        """Convert a CSV row into readable text."""
        fields = []

        for key, value in row.items():
            fields.append(
                f"{key}: {value if value is not None else ''}"
            )

        return " | ".join(fields)