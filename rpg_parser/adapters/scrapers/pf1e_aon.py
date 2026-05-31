import urllib.parse
from collections.abc import Iterable

import bs4
import requests

from rpg_parser.core.ports import FetchRequest, ScrapeRequest


class PF1eAoNSpellScraper:
    """Discovers Archives of Nethys PF1e spell detail pages from the main spell list."""

    base_url = "https://aonprd.com/"
    default_spells_url = "https://aonprd.com/Spells.aspx?Class=All"

    def discover(self, request: ScrapeRequest) -> Iterable[FetchRequest]:
        limit = request.limit
        url = request.location or self.default_spells_url

        # Make request to the Spells page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        seen = set()
        count = 0

        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if not href or "SpellDisplay.aspx" not in href:
                continue

            full_url = urllib.parse.urljoin(self.base_url, href)
            key = self._dedupe_key(full_url)

            if key in seen:
                continue

            seen.add(key)

            yield FetchRequest(location=full_url)
            count += 1

            if limit is not None and count >= limit:
                break

    def _dedupe_key(self, url: str) -> tuple[str, str]:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        for key, values in query.items():
            if key.lower() == "itemname" and values and values[0]:
                item_name = " ".join(values[0].split()).lower()
                return ("itemname", item_name)

        return ("url", url)
