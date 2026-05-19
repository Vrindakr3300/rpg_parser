import re
from typing import Any

from bs4 import BeautifulSoup

from rpg_parser.core.ports import RawDocument


def _derive_spell_id(name: str) -> str:
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class PF1eAoNSpellHtmlParser:
    """Parses PF1e spell detail pages from Archives of Nethys HTML."""

    def parse(self, document: RawDocument) -> dict[str, Any]:
        soup = BeautifulSoup(document.content, "html.parser")
        spell_data = {}

        target_span = None
        for span in soup.find_all("span", id=re.compile(r"^MainContent_DataListTypes_LabelName_\d+")):
            if span.find("h1", class_="title"):
                target_span = span
                break

        if not target_span:
            # Fallback to the whole document if we can't find the expected container
            target_span = soup.find(id="ctl00_MainContent_DataListTypes") or soup

        title_h1 = target_span.find("h1", class_="title")
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
            sibling = target_span.contents[0] if target_span.contents else None

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
