from collections.abc import Iterable
from urllib.parse import urljoin

from rpg_parser.adapters.fetchers.aon import AoNElasticsearchClient
from rpg_parser.core.ports import FetchRequest, ScrapeRequest


class AoNSpellScraper:
    """Discovers Archives of Nethys PF2e spell detail pages."""

    base_url = "https://2e.aonprd.com/"

    def __init__(self, client: AoNElasticsearchClient | None = None):
        self.client = client or AoNElasticsearchClient()

    def discover(self, request: ScrapeRequest) -> Iterable[FetchRequest]:
        filters = request.filters or {}
        tradition = filters.get("tradition")
        size = request.limit or 1000
        base_url = request.location or self.base_url

        seen = set()
        for record in self.client.fetch_spells_bulk(tradition=tradition, size=size):
            url = self._spell_url(record, base_url)
            if not url or url in seen:
                continue
            seen.add(url)
            yield FetchRequest(location=url, params={"record": record})

    def _spell_url(self, record: dict, base_url: str) -> str | None:
        for key in ["url", "href", "link"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return urljoin(base_url, value)

        aon_id = record.get("id") or record.get("ID")
        if aon_id:
            return urljoin(base_url, f"Spells.aspx?ID={aon_id}")

        return None
