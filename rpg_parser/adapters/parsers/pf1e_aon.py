import re
import urllib.parse
from typing import Any

from bs4 import BeautifulSoup

from rpg_parser.core.ports import RawDocument


def _derive_spell_id(name: str) -> str:
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _normalize_name(name: str) -> str:
    # Same normalization the scraper uses to dedupe ItemName links, so the
    # link side and the parser side agree on what counts as the "same" spell.
    return " ".join(name.split()).lower()


def _requested_item_name(source: str) -> str | None:
    """Extract the normalized ItemName query param from the fetched URL, if any."""
    if not source:
        return None
    query = urllib.parse.parse_qs(urllib.parse.urlparse(source).query)
    for key, values in query.items():
        if key.lower() == "itemname" and values and values[0]:
            return _normalize_name(values[0])
    return None


class PF1eAoNSpellHtmlParser:
    """Parses PF1e spell detail pages from Archives of Nethys HTML."""

    def parse(self, document: RawDocument) -> dict[str, Any]:
        soup = BeautifulSoup(document.content, "html.parser")
        spell_data = {}

        # A single SpellDisplay.aspx page can bundle several spells as consecutive
        # <h1 class="title"> headings. Pick the one matching the requested ItemName
        # so each link yields its own spell, rather than always taking the first.
        container = (
            soup.find(id="MainContent_DataListTypes")
            or soup.find(id="ctl00_MainContent_DataListTypes")
            or soup
        )
        title_h1s = container.find_all("h1", class_="title")

        title_h1 = None
        requested = _requested_item_name(document.source)
        if requested:
            for h1 in title_h1s:
                if _normalize_name(h1.get_text(strip=True)) == requested:
                    title_h1 = h1
                    break

        if title_h1 is None and title_h1s:
            # No ItemName in the source URL, or no title matched: fall back to the
            # first spell on the page (preserves the original behavior).
            title_h1 = title_h1s[0]

        if title_h1:
            for img in title_h1.find_all("img"):
                img.extract()
            spell_data["Name"] = title_h1.get_text(strip=True)

        known_keys = [
            "Source", "School", "Level", "Casting Time", "Components",
            "Range", "Area", "Target", "Effect", "Duration", "Saving Throw",
            "Spell Resistance", "Bloodline", "Domain", "Deity"
        ]

        if title_h1:
            sibling = title_h1.next_sibling
        else:
            sibling = container.contents[0] if getattr(container, "contents", None) else None

        desc_heading = None

        while sibling:
            if sibling.name in ["h1", "h2"] and "title" in sibling.get("class", []):
                break

            if sibling.name == "b":
                key = sibling.get_text(strip=True)
                if key in known_keys or key.endswith("Domain") or key.endswith("Bloodline"):
                    value_parts = []
                    val_sibling = sibling.next_sibling
                    while val_sibling:
                        if val_sibling.name in ["br", "hr", "h1", "h2", "h3", "table"]:
                            break
                        if val_sibling.name == "b" and val_sibling.get_text(strip=True) in known_keys:
                            break

                        if isinstance(val_sibling, str):
                            value_parts.append(val_sibling.strip())
                        else:
                            value_parts.append(val_sibling.get_text(strip=True))
                        val_sibling = val_sibling.next_sibling

                    value = " ".join(p for p in value_parts if p).strip()
                    value = re.sub(r"^[;,]\s*", "", value)
                    spell_data[key] = value

            if sibling.name == "h3" and sibling.get_text(strip=True) and "Description" in sibling.get_text(strip=True):
                desc_heading = sibling

            sibling = sibling.next_sibling

        if desc_heading:
            desc_parts = []
            sibling = desc_heading.next_sibling
            while sibling:
                if sibling.name in ["h1", "h2"]:  # Reached alternate spell
                    break
                if isinstance(sibling, str):
                    text = sibling.strip()
                    if text:
                        desc_parts.append(text)
                elif sibling.name != "br":
                    text = sibling.get_text(strip=True)
                    if text:
                        desc_parts.append(text)
                sibling = sibling.next_sibling

            description = "\n".join(desc_parts).strip()
            if description:
                spell_data["Description"] = description

        return {"id": _derive_spell_id(spell_data.get("Name", "")), **spell_data}
