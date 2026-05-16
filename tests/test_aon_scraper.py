import unittest

from rpg_parser.adapters.scrapers.aon import AoNSpellScraper
from rpg_parser.core.ports import ScrapeRequest


class FakeAoNClient:
    def fetch_spells_bulk(self, tradition=None, size=1000):
        self.tradition = tradition
        self.size = size
        return [
            {"name": "Fireball", "url": "Spells.aspx?ID=1530"},
            {"name": "Duplicate Fireball", "url": "Spells.aspx?ID=1530"},
            {"name": "Fallback ID", "id": 123},
        ]


class TestAoNSpellScraper(unittest.TestCase):
    def test_discover_returns_unique_fetch_requests(self):
        client = FakeAoNClient()
        scraper = AoNSpellScraper(client=client)

        requests = list(
            scraper.discover(
                ScrapeRequest(
                    location="https://2e.aonprd.com/",
                    filters={"tradition": "arcane"},
                    limit=10,
                )
            )
        )

        self.assertEqual(client.tradition, "arcane")
        self.assertEqual(client.size, 10)
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].location, "https://2e.aonprd.com/Spells.aspx?ID=1530")
        self.assertEqual(requests[1].location, "https://2e.aonprd.com/Spells.aspx?ID=123")


if __name__ == "__main__":
    unittest.main()
