from typing import Any

from rpg_parser.core.ports import ExportTarget, FetchRequest, PipelineSpec


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
