from collections.abc import Iterable

import requests

from rpg_parser.adapters.fetchers.open5e import OPEN5E_USER_AGENT
from rpg_parser.core.ports import FetchRequest, ScrapeRequest


class Dnd5eOpen5eSpellScraper:
    """Discovers D&D 5e SRD spells from the Open5e v2 list endpoint.

    The list endpoint returns complete spell objects (paginated via a ``next`` URL),
    so each discovered spell is embedded in ``FetchRequest.params['record']``. The
    Open5eJsonFetcher returns that embedded record directly, avoiding a redundant
    detail GET per spell.
    """

    base_url = "https://api.open5e.com/v2/spells/"

    def __init__(self, document_key: str = "srd-2024", timeout: float = 30.0):
        self.document_key = document_key
        self.timeout = timeout

    def discover(self, request: ScrapeRequest) -> Iterable[FetchRequest]:
        limit = request.limit
        filters = request.filters or {}
        document_key = filters.get("document_key") or self.document_key

        url = request.location or f"{self.base_url}?document__key={document_key}&limit=50"

        headers = {"User-Agent": OPEN5E_USER_AGENT, "Accept": "application/json"}
        seen: set[str] = set()
        count = 0

        while url:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for spell in data.get("results", []):
                key = spell.get("key")
                if not key or key in seen:
                    continue
                seen.add(key)

                detail_url = f"{self.base_url}{key}/"
                yield FetchRequest(location=detail_url, params={"record": spell})
                count += 1

                if limit is not None and count >= limit:
                    return

            url = data.get("next")
