import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rpg_parser.adapters.scrapers.open5e import Dnd5eOpen5eSpellScraper
from rpg_parser.core.ports import ScrapeRequest


def _response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class TestDnd5eOpen5eSpellScraper(unittest.TestCase):
    def setUp(self):
        samples_dir = Path(__file__).parent.parent / "samples"
        with open(samples_dir / "sample_dnd5e_open5e_list.json", "r", encoding="utf-8") as f:
            self.list_payload = json.load(f)  # 3 results, next=None

    @patch("rpg_parser.adapters.scrapers.open5e.requests.get")
    def test_discover_yields_requests_with_embedded_records(self, mock_get: MagicMock):
        mock_get.return_value = _response(self.list_payload)

        scraper = Dnd5eOpen5eSpellScraper()
        results = list(scraper.discover(ScrapeRequest()))

        self.assertEqual(len(results), 3)
        self.assertEqual(
            results[0].location,
            "https://api.open5e.com/v2/spells/srd-2024_acid-arrow/",
        )
        # Each request embeds the full spell record so the fetcher skips a detail GET.
        self.assertEqual(results[0].params["record"]["name"], "Acid Arrow")
        self.assertEqual(results[0].params["record"]["key"], "srd-2024_acid-arrow")

        # The default discovery URL filters to the 2024 SRD.
        called_url = mock_get.call_args.args[0]
        self.assertIn("document__key=srd-2024", called_url)

    @patch("rpg_parser.adapters.scrapers.open5e.requests.get")
    def test_discover_respects_limit(self, mock_get: MagicMock):
        mock_get.return_value = _response(self.list_payload)

        scraper = Dnd5eOpen5eSpellScraper()
        results = list(scraper.discover(ScrapeRequest(limit=2)))

        self.assertEqual(len(results), 2)

    @patch("rpg_parser.adapters.scrapers.open5e.requests.get")
    def test_discover_follows_pagination(self, mock_get: MagicMock):
        page1 = {
            "next": "https://api.open5e.com/v2/spells/?page=2",
            "results": [{"key": "srd-2024_a", "name": "A"}],
        }
        page2 = {
            "next": None,
            "results": [{"key": "srd-2024_b", "name": "B"}],
        }
        mock_get.side_effect = [_response(page1), _response(page2)]

        scraper = Dnd5eOpen5eSpellScraper()
        results = list(scraper.discover(ScrapeRequest()))

        self.assertEqual(len(results), 2)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(
            [r.params["record"]["key"] for r in results],
            ["srd-2024_a", "srd-2024_b"],
        )

    @patch("rpg_parser.adapters.scrapers.open5e.requests.get")
    def test_discover_dedupes_by_key(self, mock_get: MagicMock):
        payload = {
            "next": None,
            "results": [
                {"key": "srd-2024_a", "name": "A"},
                {"key": "srd-2024_a", "name": "A again"},
                {"key": "srd-2024_b", "name": "B"},
            ],
        }
        mock_get.return_value = _response(payload)

        scraper = Dnd5eOpen5eSpellScraper()
        results = list(scraper.discover(ScrapeRequest()))

        self.assertEqual(len(results), 2)

    @patch("rpg_parser.adapters.scrapers.open5e.requests.get")
    def test_document_key_override_via_filters(self, mock_get: MagicMock):
        mock_get.return_value = _response({"next": None, "results": []})

        scraper = Dnd5eOpen5eSpellScraper()
        list(scraper.discover(ScrapeRequest(filters={"document_key": "srd-2014"})))

        called_url = mock_get.call_args.args[0]
        self.assertIn("document__key=srd-2014", called_url)


if __name__ == "__main__":
    unittest.main()
