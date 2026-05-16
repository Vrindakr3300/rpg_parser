from rpg_parser.adapters.parsers.pf2e_aon import PF2eAoNSpellHtmlParser
from rpg_parser.core.ports import RawDocument


def parse_aon_spell(html: str) -> dict:
    """
    Parses an Archives of Nethys spell page and extracts structured data.
    """
    return PF2eAoNSpellHtmlParser().parse(RawDocument(content=html, source="inline"))
