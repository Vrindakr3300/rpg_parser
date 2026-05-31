import os
import unittest

from rpg_parser.adapters.fetchers.aon import AoNElasticsearchClient


@unittest.skipUnless(
    os.environ.get("RPG_PARSER_RUN_INTEGRATION"),
    "live AoN integration test; set RPG_PARSER_RUN_INTEGRATION=1 to run",
)
class TestScraperIntegration(unittest.TestCase):
    """Hits the live elasticsearch.aonprd.com endpoint; requires network."""

    def test_fetch_fireball(self):
        """
        Integration test to verify that we can fetch the 'Fireball' spell
        from the Archives of Nethys Elasticsearch API.
        """
        spell_name = "Fireball"

        # This will raise an exception if it fails
        spell_data = AoNElasticsearchClient().fetch_spell_by_name(spell_name)

        # Verify basic properties of the Fireball spell
        self.assertIsNotNone(spell_data)
        self.assertEqual(spell_data.get("name"), spell_name)
        self.assertEqual(spell_data.get("type"), "Spell")

        # Fireball should definitely have the 'fire' and 'evocation' traits
        traits = [trait.lower() for trait in spell_data.get("trait", [])]
        self.assertIn("fire", traits)

        # Check tradition
        traditions = [tradition.lower() for tradition in spell_data.get("tradition", [])]
        self.assertIn("arcane", traditions)
        self.assertIn("primal", traditions)

if __name__ == "__main__":
    unittest.main()
