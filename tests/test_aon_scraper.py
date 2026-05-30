import unittest

from rpg_parser.adapters.fetchers.aon import AoNElasticsearchClient
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
            {"name": "Excluded Spell", "id": 789, "exclude_from_search": True},
            {"name": "Fireball", "id": 2026, "url": "Spells.aspx?ID=2026"},
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
        # It skips: Duplicate Fireball, Fireball Variant, Duplicate Fallback ID, Legacy Fireball (has remaster_id),
        # Excluded Spell (exclude_from_search is True), and the duplicate Fireball (same name)
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[0].location, "https://2e.aonprd.com/Spells.aspx?ID=1530")
        self.assertEqual(requests[1].location, "https://2e.aonprd.com/Spells.aspx?ID=123")
        self.assertEqual(requests[2].location, "https://2e.aonprd.com/Spells.aspx?ID=456")

    def test_discover_clamps_query_size_to_window(self):
        # The default --limit=5000 makes max(5000, limit*3) == 15000, which exceeds
        # AoN's index.max_result_window (10000) and was rejected with a 400.
        client = FakeAoNClient()
        scraper = AoNSpellScraper(client=client)

        list(scraper.discover(ScrapeRequest(limit=5000)))

        self.assertEqual(client.size, AoNElasticsearchClient.MAX_RESULT_WINDOW)


class TestAoNElasticsearchClient(unittest.TestCase):
    def test_fetch_spells_bulk_clamps_size_to_window(self):
        client = AoNElasticsearchClient()
        captured = {}

        def fake_post(payload):
            captured["payload"] = payload
            return {"hits": {"hits": []}}

        client._post = fake_post
        client.fetch_spells_bulk(size=15000)

        self.assertEqual(
            captured["payload"]["size"], AoNElasticsearchClient.MAX_RESULT_WINDOW
        )


if __name__ == "__main__":
    unittest.main()
