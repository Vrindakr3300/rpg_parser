import unittest

from rpg_parser.adapters.exporters.json_file import JsonFileExporter
from rpg_parser.adapters.fetchers.aon import AoNHtmlFetcher
from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.adapters.scrapers.aon import AoNSpellScraper
from rpg_parser.registry import get_pipeline, get_scrape_pipeline


class TestRegistry(unittest.TestCase):
    def test_get_pipeline_resolves_pf2e_spell_aon_html(self):
        pipeline = get_pipeline("pf2e", "spell", "aon-html")

        self.assertIsInstance(pipeline.fetcher, AoNHtmlFetcher)
        self.assertIsInstance(pipeline.parser, PF2eAoNSpellHtmlParser)
        self.assertIsInstance(pipeline.exporter, JsonFileExporter)

    def test_get_pipeline_rejects_unknown_pipeline(self):
        with self.assertRaises(ValueError):
            get_pipeline("unknown", "spell", "aon-html")

    def test_get_scrape_pipeline_resolves_pf2e_spell_aon_html(self):
        pipeline = get_scrape_pipeline("pf2e", "spell", "aon-html")

        self.assertIsInstance(pipeline.scraper, AoNSpellScraper)
        self.assertIsInstance(pipeline.fetcher, AoNHtmlFetcher)
        self.assertIsInstance(pipeline.parser, PF2eAoNSpellHtmlParser)
        self.assertIsInstance(pipeline.exporter, JsonFileExporter)


if __name__ == "__main__":
    unittest.main()
