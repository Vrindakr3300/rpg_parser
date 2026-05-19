import unittest
from unittest.mock import MagicMock, patch

from rpg_parser.adapters.scrapers.pf1e_aon import PF1eAoNSpellScraper
from rpg_parser.core.ports import ScrapeRequest


class TestPF1eAoNSpellScraper(unittest.TestCase):
    @patch("rpg_parser.adapters.scrapers.pf1e_aon.requests.get")
    def test_discover_extracts_spell_links(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <a href="SpellDisplay.aspx?ItemName=Fireball">Fireball</a>
                <a href="SpellDisplay.aspx?ItemName=Magic%20Missile">Magic Missile</a>
                <a href="OtherPage.aspx">Not a spell</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        scraper = PF1eAoNSpellScraper()
        request = ScrapeRequest()
        
        results = list(scraper.discover(request))
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].location, "https://aonprd.com/SpellDisplay.aspx?ItemName=Fireball")
        self.assertEqual(results[1].location, "https://aonprd.com/SpellDisplay.aspx?ItemName=Magic%20Missile")
        
        mock_get.assert_called_once_with(
            "https://aonprd.com/Spells.aspx?Class=All",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    @patch("rpg_parser.adapters.scrapers.pf1e_aon.requests.get")
    def test_discover_respects_limit(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <a href="SpellDisplay.aspx?ItemName=Fireball">Fireball</a>
                <a href="SpellDisplay.aspx?ItemName=Magic%20Missile">Magic Missile</a>
                <a href="SpellDisplay.aspx?ItemName=Fly">Fly</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        scraper = PF1eAoNSpellScraper()
        request = ScrapeRequest(limit=2)
        
        results = list(scraper.discover(request))
        
        self.assertEqual(len(results), 2)

    @patch("rpg_parser.adapters.scrapers.pf1e_aon.requests.get")
    def test_discover_deduplicates_links(self, mock_get: MagicMock):
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <a href="SpellDisplay.aspx?ItemName=Fireball">Fireball</a>
                <a href="SpellDisplay.aspx?ItemName=Fireball">Fireball again</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        scraper = PF1eAoNSpellScraper()
        request = ScrapeRequest()
        
        results = list(scraper.discover(request))
        
        self.assertEqual(len(results), 1)

if __name__ == "__main__":
    unittest.main()
