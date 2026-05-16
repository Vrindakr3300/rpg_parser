from typing import Any

import requests

from rpg_parser.core.ports import FetchRequest, RawDocument


AON_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


class AoNHtmlFetcher:
    """Fetches raw Archives of Nethys HTML pages."""

    def fetch(self, request: FetchRequest) -> RawDocument:
        response = requests.get(request.location, headers={"User-Agent": AON_USER_AGENT})
        response.raise_for_status()
        return RawDocument(
            content=response.text,
            source=request.location,
            media_type="text/html",
        )


class AoNElasticsearchClient:
    """Client for the Archives of Nethys Elasticsearch endpoint."""

    url = "https://elasticsearch.aonprd.com/aon/_search?stats=search"

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def fetch_spells_bulk(self, tradition: str | None = "primal", size: int = 1000) -> list[dict[str, Any]]:
        filters = [{"term": {"type": {"value": "spell"}}}]
        if tradition:
            filters.insert(0, {"term": {"tradition": {"value": tradition.lower()}}})

        payload = {
            "query": {
                "bool": {
                    "filter": filters
                }
            },
            "size": size,
            "_source": True,
        }

        data = self._post(payload)
        hits = data.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}) for hit in hits]

    def fetch_spell_by_name(self, name: str) -> dict[str, Any]:
        payload = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"name.keyword": {"value": name}}},
                        {"term": {"type": {"value": "spell"}}},
                    ]
                }
            },
            "size": 1,
            "_source": True,
        }

        data = self._post(payload)
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            raise ValueError(f"Spell not found: {name}")

        return hits[0].get("_source", {})
