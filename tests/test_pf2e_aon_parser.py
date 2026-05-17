import unittest

from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.core.ports import RawDocument


def _doc(body: str) -> RawDocument:
    html = f'<div id="ctl00_MainContent_DetailedOutput">{body}</div>'
    return RawDocument(content=html, source="test")


class TestPF2eAoNSpellHtmlParserHeightened(unittest.TestCase):
    def test_heightened_entries_collected_as_array(self):
        body = (
            '<h1 class="title">Aerial Form</h1>'
            '<hr />Description goes here.<hr />'
            '<b>Heightened (5th)</b> text1<br />'
            '<b>Heightened (6th)</b> text2'
        )
        result = PF2eAoNSpellHtmlParser().parse(_doc(body))

        self.assertEqual(
            result["heightened"],
            [
                {"label": "5th", "text": "text1"},
                {"label": "6th", "text": "text2"},
            ],
        )
        self.assertNotIn("Heightened (5th)", result)
        self.assertNotIn("Heightened (6th)", result)

    def test_heightened_increment_label(self):
        body = (
            '<h1 class="title">Hydraulic Torrent</h1>'
            '<hr />Description goes here.<hr />'
            '<b>Heightened (+1)</b> The damage increases by 2d8.'
        )
        result = PF2eAoNSpellHtmlParser().parse(_doc(body))

        self.assertEqual(
            result["heightened"],
            [{"label": "+1", "text": "The damage increases by 2d8."}],
        )

    def test_no_heightened_key_when_absent(self):
        body = (
            '<h1 class="title">Plain Spell</h1>'
            '<hr />Just a description, no heightening.'
        )
        result = PF2eAoNSpellHtmlParser().parse(_doc(body))

        self.assertNotIn("heightened", result)


if __name__ == "__main__":
    unittest.main()
