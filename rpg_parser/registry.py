from rpg_parser.adapters.exporters.json_file import JsonFileExporter
from rpg_parser.adapters.fetchers.aon import AoNHtmlFetcher
from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.adapters.scrapers.aon import AoNSpellScraper
from rpg_parser.core.ports import PipelineSpec, ScrapePipelineSpec


PIPELINES = {
    ("pf2e", "spell", "aon-html"): PipelineSpec(
        fetcher=AoNHtmlFetcher(),
        parser=PF2eAoNSpellHtmlParser(),
        exporter=JsonFileExporter(),
    ),
}

SCRAPE_PIPELINES = {
    ("pf2e", "spell", "aon-html"): ScrapePipelineSpec(
        scraper=AoNSpellScraper(),
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


def get_scrape_pipeline(system: str, content_type: str, source: str) -> ScrapePipelineSpec:
    key = (system.lower(), content_type.lower(), source.lower())
    try:
        return SCRAPE_PIPELINES[key]
    except KeyError as exc:
        available = ", ".join("/".join(parts) for parts in sorted(SCRAPE_PIPELINES))
        raise ValueError(
            f"Unsupported scrape pipeline: {'/'.join(key)}. Available scrape pipelines: {available}"
        ) from exc
