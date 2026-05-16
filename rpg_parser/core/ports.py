from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class FetchRequest:
    """Input needed by a fetcher adapter."""

    location: str
    params: dict[str, Any] | None = None


@dataclass(frozen=True)
class RawDocument:
    """Raw data returned by a fetcher before parsing."""

    content: str
    source: str
    media_type: str = "text/html"


@dataclass(frozen=True)
class ExportTarget:
    """Destination for an exporter adapter."""

    location: str


class Fetcher(Protocol):
    def fetch(self, request: FetchRequest) -> RawDocument:
        """Fetch raw content from an external source."""


class Parser(Protocol):
    def parse(self, document: RawDocument) -> dict[str, Any]:
        """Parse raw content into structured data."""


class Exporter(Protocol):
    def export(self, data: dict[str, Any], target: ExportTarget) -> None:
        """Export structured data to a target destination."""


@dataclass(frozen=True)
class PipelineSpec:
    fetcher: Fetcher
    parser: Parser
    exporter: Exporter
