from rpg_parser.adapters.exporters.json_file import JsonFileExporter
from rpg_parser.adapters.fetchers.aon import AoNHtmlFetcher
from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.core.ports import PipelineSpec


PIPELINES = {
    ("pf2e", "spell", "aon-html"): PipelineSpec(
        fetcher=AoNHtmlFetcher(),
        parser=PF2eAoNSpellHtmlParser(),
        exporter=JsonFileExporter(),
    ),
}


def get_pipeline(system: str, content_type: str, source: str) -> PipelineSpec:
    key = (system.lower(), content_type.lower(), source.lower())
    try:
        return PIPELINES[key]
    except KeyError as exc:
        available = ", ".join("/".join(parts) for parts in sorted(PIPELINES))
        raise ValueError(
            f"Unsupported pipeline: {'/'.join(key)}. Available pipelines: {available}"
        ) from exc
