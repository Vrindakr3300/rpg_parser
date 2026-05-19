import unittest
from pathlib import Path

from rpg_parser.adapters.parsers.pf1e_aon import PF1eAoNSpellHtmlParser
from rpg_parser.core.ports import RawDocument


class TestPF1eAoNSpellHtmlParser(unittest.TestCase):
    def setUp(self):
        self.parser = PF1eAoNSpellHtmlParser()
        sample_path = Path(__file__).parent.parent / "sample_pf1e_spell.html"
        with open(sample_path, "r", encoding="utf-8") as f:
            self.sample_html = f.read()

    def test_parse_fireball(self):
        doc = RawDocument(content=self.sample_html, source="test")
        result = self.parser.parse(doc)

        self.assertEqual(result["id"], "fireball")
        self.assertEqual(result["Name"], "Fireball")
        self.assertEqual(result["Source"], "PRPG Core Rulebook pg. 283")
        self.assertEqual(result["School"], "evocation [ fire ];")
        self.assertEqual(result["Level"], "arcanist 3, bloodrager 3, magus 3, occultist 3, sorcerer 3, wizard 3")
        self.assertEqual(result["Casting Time"], "1 standard action")
        self.assertEqual(result["Components"], "V, S, M (a ball of bat guano and sulfur)")
        self.assertEqual(result["Range"], "long (400 ft. + 40 ft./level)")
        self.assertEqual(result["Area"], "20-ft.-radius spread")
        self.assertEqual(result["Duration"], "instantaneous")
        self.assertEqual(result["Saving Throw"], "Reflex half;")
        self.assertEqual(result["Spell Resistance"], "yes")

        # Check description
        self.assertIn("A\nfireball\nspell generates a searing explosion", result["Description"])
        self.assertIn("The\nfireball\nsets fire to combustibles", result["Description"])
        self.assertNotIn("Mythic Fireball", result["Description"])
        self.assertNotIn("Controlled Fireball", result.get("Description", ""))
