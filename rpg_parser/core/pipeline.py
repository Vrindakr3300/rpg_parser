import time
from collections.abc import Callable
from typing import Any

from rpg_parser.core.ports import ExportTarget, FetchRequest, PipelineSpec, ScrapePipelineSpec, ScrapeRequest

SCRAPE_REQUEST_DELAY_SECONDS = 1.0


def run_pipeline(
    spec: PipelineSpec,
    request: FetchRequest,
    target: ExportTarget | None = None,
) -> dict[str, Any]:
    raw_document = spec.fetcher.fetch(request)
    data = spec.parser.parse(raw_document)

    if target is not None:
        spec.exporter.export(data, target)

    return data


def run_scrape_pipeline(
    spec: ScrapePipelineSpec,
    request: ScrapeRequest,
    target_factory: Callable[[dict[str, Any], int, FetchRequest], ExportTarget | None] | None = None,
) -> list[dict[str, Any]]:
    records = []

    for index, fetch_request in enumerate(spec.scraper.discover(request), start=1):
        if index > 1:
            time.sleep(SCRAPE_REQUEST_DELAY_SECONDS)
        raw_document = spec.fetcher.fetch(fetch_request)
        data = spec.parser.parse(raw_document)
        records.append(data)

        if target_factory is not None:
            target = target_factory(data, index, fetch_request)
            if target is not None:
                spec.exporter.export(data, target)

    return records
