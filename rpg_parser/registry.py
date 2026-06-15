from rpg_parser.adapters.exporters.json_file import JsonFileExporter
from rpg_parser.adapters.fetchers.aon import AoNHtmlFetcher
from rpg_parser.adapters.fetchers.open5e import Open5eJsonFetcher
from rpg_parser.adapters.parsers.dnd5e_open5e import Dnd5eOpen5eSpellParser
from rpg_parser.adapters.parsers.pf1e_aon import PF1eAoNSpellHtmlParser
from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.adapters.scrapers.aon import AoNSpellScraper
from rpg_parser.adapters.scrapers.open5e import Dnd5eOpen5eSpellScraper
from rpg_parser.adapters.scrapers.pf1e_aon import PF1eAoNSpellScraper
from rpg_parser.core.ports import PipelineSpec, ScrapePipelineSpec

PIPELINES = {
    ("pf2e", "spell", "aon-html"): PipelineSpec(
        fetcher=AoNHtmlFetcher(),
        parser=PF2eAoNSpellHtmlParser(),
        exporter=JsonFileExporter(),
    ),
    ("pf1e", "spell", "aon-html"): PipelineSpec(
        fetcher=AoNHtmlFetcher(),
        parser=PF1eAoNSpellHtmlParser(),
        exporter=JsonFileExporter(),
    ),
    ("dnd5e", "spell", "open5e"): PipelineSpec(
        fetcher=Open5eJsonFetcher(),
        parser=Dnd5eOpen5eSpellParser(),
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
    ("pf1e", "spell", "aon-html"): ScrapePipelineSpec(
        scraper=PF1eAoNSpellScraper(),
        fetcher=AoNHtmlFetcher(),
        parser=PF1eAoNSpellHtmlParser(),
        exporter=JsonFileExporter(),
    ),
    ("dnd5e", "spell", "open5e"): ScrapePipelineSpec(
        scraper=Dnd5eOpen5eSpellScraper(),
        fetcher=Open5eJsonFetcher(),
        parser=Dnd5eOpen5eSpellParser(),
        exporter=JsonFileExporter(),
    ),
}


DEFAULT_SOURCE = "aon-html"
DEFAULT_SOURCES_BY_SYSTEM = {"dnd5e": "open5e"}


def default_source(system: str) -> str:
    """Return the default `--source` for a system when none is supplied."""
    return DEFAULT_SOURCES_BY_SYSTEM.get(system.lower(), DEFAULT_SOURCE)


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
