from collections.abc import Iterable
from urllib.parse import parse_qs, urljoin, urlparse

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
        size = request.limit or 5000
        base_url = request.location or self.base_url

        seen = set()
        for record in self.client.fetch_spells_bulk(tradition=tradition, size=size):
            url = self._spell_url(record, base_url)
            key = self._dedupe_key(record, url) if url else None
            if not url or key in seen:
                continue
            seen.add(key)
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

    def _dedupe_key(self, record: dict, url: str) -> tuple[str, str]:
        for key in ["id", "ID"]:
            value = record.get(key)
            if value:
                return ("id", str(value).strip())

        query = parse_qs(urlparse(url).query)
        for key, values in query.items():
            if key.lower() == "id" and values and values[0]:
                return ("id", values[0].strip())

        return ("url", url)
