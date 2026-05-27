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
            {"name": "Fireball Variant", "url": "Spells.aspx?ID=1530&NoRedirect=1"},
            {"name": "Fallback ID", "id": 123},
            {"name": "Duplicate Fallback ID", "ID": 123, "url": "Spells.aspx?ID=999"},
            {"name": "Legacy Fireball", "url": "Spells.aspx?ID=119", "remaster_id": ["spell-1530"]},
            {"name": "Prefixed ID Spell", "id": "spell-456"},
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
        self.assertEqual(client.size, 5000)
        # Should contain: Fireball (ID 1530), Fallback ID (ID 123), and Prefixed ID Spell (ID 456)
        # It skips: Duplicate Fireball, Fireball Variant, Duplicate Fallback ID, and Legacy Fireball (has remaster_id)
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[0].location, "https://2e.aonprd.com/Spells.aspx?ID=1530")
        self.assertEqual(requests[1].location, "https://2e.aonprd.com/Spells.aspx?ID=123")
        self.assertEqual(requests[2].location, "https://2e.aonprd.com/Spells.aspx?ID=456")


if __name__ == "__main__":
    unittest.main()
