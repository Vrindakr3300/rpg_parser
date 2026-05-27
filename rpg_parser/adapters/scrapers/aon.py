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
        limit = request.limit
        # Query a larger size from Elasticsearch to ensure we have enough records after filtering legacy spells
        query_size = max(5000, limit * 3) if limit else 5000
        base_url = request.location or self.base_url

        seen = set()
        seen_names = set()
        yielded_count = 0
        for record in self.client.fetch_spells_bulk(tradition=tradition, size=query_size):
            if record.get("remaster_id"):
                continue
            if record.get("exclude_from_search"):
                continue
            url = self._spell_url(record, base_url)
            key = self._dedupe_key(record, url) if url else None
            name_key = record.get("name", "").lower().strip()
            if not url or key in seen or (name_key and name_key in seen_names):
                continue
            seen.add(key)
            if name_key:
                seen_names.add(name_key)
            yield FetchRequest(location=url, params={"record": record})
            yielded_count += 1
            if limit is not None and yielded_count >= limit:
                break

    def _spell_url(self, record: dict, base_url: str) -> str | None:
        for key in ["url", "href", "link"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return urljoin(base_url, value)

        aon_id = record.get("id") or record.get("ID")
        if aon_id:
            # Strip "spell-" or other prefixes from the ID for a valid URL
            if isinstance(aon_id, str) and "-" in aon_id:
                aon_id = aon_id.split("-")[-1]
            return urljoin(base_url, f"Spells.aspx?ID={aon_id}")

        return None

    def _dedupe_key(self, record: dict, url: str) -> tuple[str, str]:
        for key in ["id", "ID"]:
            value = record.get(key)
            if value:
                val_str = str(value).strip()
                if "-" in val_str:
                    val_str = val_str.split("-")[-1]
                return ("id", val_str)

        query = parse_qs(urlparse(url).query)
        for key, values in query.items():
            if key.lower() == "id" and values and values[0]:
                return ("id", values[0].strip())

        return ("url", url)
