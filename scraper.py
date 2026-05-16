from typing import Any

from rpg_parser.adapters.fetchers.aon import AoNElasticsearchClient, AoNHtmlFetcher
from rpg_parser.core.ports import FetchRequest


def fetch_spell_html(url: str) -> str:
    """Fetches the HTML content of an Archives of Nethys spell URL."""
    return AoNHtmlFetcher().fetch(FetchRequest(location=url)).content


def fetch_spells_bulk(tradition: str = "primal", size: int = 1000) -> list[dict[str, Any]]:
    """
    Fetches spells in bulk from the Archives of Nethys Elasticsearch API.
    By default fetches 'primal' spells.
    """
    return AoNElasticsearchClient().fetch_spells_bulk(tradition=tradition, size=size)


def fetch_spell_by_name(name: str) -> dict[str, Any]:
    """
    Fetches a single spell by its exact name from the Archives of Nethys Elasticsearch API.
    """
    return AoNElasticsearchClient().fetch_spell_by_name(name)
