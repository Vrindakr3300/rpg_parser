import unittest
from scraper import fetch_spell_by_name

class TestScraperIntegration(unittest.TestCase):
    def test_fetch_fireball(self):
        """
        Integration test to verify that we can fetch the 'Fireball' spell
        from the Archives of Nethys Elasticsearch API.
        """
        spell_name = "Fireball"
        
        # This will raise an exception if it fails
        spell_data = fetch_spell_by_name(spell_name)
        
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
