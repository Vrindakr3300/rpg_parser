import unittest
from pathlib import Path

from rpg_parser.adapters.parsers.pf1e_aon import PF1eAoNSpellHtmlParser
from rpg_parser.core.ports import RawDocument


class TestPF1eAoNSpellHtmlParser(unittest.TestCase):
    def setUp(self):
        self.parser = PF1eAoNSpellHtmlParser()
        samples_dir = Path(__file__).parent.parent / "samples"
        with open(samples_dir / "sample_pf1e_spell.html", "r", encoding="utf-8") as f:
            self.sample_html = f.read()
        # A page that bundles three spells: Shield Other (_0),
        # Shield Companion (AA) (_1), Sympathetic Wounds (_2).
        with open(samples_dir / "sample_pf1e_bundled_spell.html", "r", encoding="utf-8") as f:
            self.bundled_html = f.read()
        # A real AoN page whose malformed table markup makes html.parser eject all
        # but the first bundled <h1 class="title"> out of MainContent_DataListTypes.
        # Bundles four spells: Curse Terrain, Lesser / Curse Terrain /
        # Curse Terrain, Greater / Curse Terrain, Supreme.
        with open(samples_dir / "sample_pf1e_curse_terrain.html", "r", encoding="utf-8") as f:
            self.curse_terrain_html = f.read()

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

    def test_bundled_page_selects_non_first_sibling(self):
        # A bundled page is fetched once per linked spell; the parser must pick
        # the spell matching the requested ItemName, not always the first one.
        doc = RawDocument(
            content=self.bundled_html,
            source="https://aonprd.com/SpellDisplay.aspx?ItemName=Shield Companion (AA)",
        )
        result = self.parser.parse(doc)

        self.assertEqual(result["id"], "shield-companion-aa")
        self.assertEqual(result["Name"], "Shield Companion (AA)")

    def test_bundled_page_selects_first_spell(self):
        doc = RawDocument(
            content=self.bundled_html,
            source="https://aonprd.com/SpellDisplay.aspx?ItemName=Shield Other",
        )
        result = self.parser.parse(doc)

        self.assertEqual(result["id"], "shield-other")
        self.assertEqual(result["Name"], "Shield Other")

    def test_bundled_page_selects_last_sibling(self):
        doc = RawDocument(
            content=self.bundled_html,
            source="https://aonprd.com/SpellDisplay.aspx?ItemName=Sympathetic Wounds",
        )
        result = self.parser.parse(doc)

        self.assertEqual(result["id"], "sympathetic-wounds")
        self.assertEqual(result["Name"], "Sympathetic Wounds")

    def test_bundled_page_unknown_item_name_falls_back_to_first(self):
        doc = RawDocument(
            content=self.bundled_html,
            source="https://aonprd.com/SpellDisplay.aspx?ItemName=Nonexistent Spell",
        )
        result = self.parser.parse(doc)

        self.assertEqual(result["id"], "shield-other")

    def test_bundled_page_with_sibling_headings_outside_container(self):
        # Regression: on the real Curse Terrain page, html.parser ejects every bundled
        # heading except the first out of MainContent_DataListTypes. Searching only that
        # container saw a single heading, so all four ItemName links fell back to the
        # first spell, producing four identical "Curse Terrain, Lesser" records (and
        # silently dropping the other three). Each link must resolve to its own spell.
        cases = {
            "Curse Terrain, Lesser": ("curse-terrain-lesser", "Curse Terrain, Lesser"),
            "Curse Terrain": ("curse-terrain", "Curse Terrain"),
            "Curse Terrain, Greater": ("curse-terrain-greater", "Curse Terrain, Greater"),
            "Curse Terrain, Supreme": ("curse-terrain-supreme", "Curse Terrain, Supreme"),
        }
        ids = []
        for item_name, (expected_id, expected_name) in cases.items():
            doc = RawDocument(
                content=self.curse_terrain_html,
                source=f"https://aonprd.com/SpellDisplay.aspx?ItemName={item_name}",
            )
            result = self.parser.parse(doc)
            self.assertEqual(result["id"], expected_id, item_name)
            self.assertEqual(result["Name"], expected_name, item_name)
            ids.append(result["id"])

        # All four links must yield distinct records, not duplicates of the first.
        self.assertEqual(len(set(ids)), 4)
