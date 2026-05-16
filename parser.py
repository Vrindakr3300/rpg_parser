from bs4 import BeautifulSoup
import re

def parse_aon_spell(html: str) -> dict:
    """
    Parses an Archives of Nethys spell page and extracts structured data.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # The main content container in AoN
    main_content = soup.find(id='ctl00_MainContent_DetailedOutput') or soup.find(class_='main') or soup
    
    spell_data = {}
    
    # 1. Name, Level, and Actions
    title_h1 = main_content.find('h1', class_='title')
    if title_h1 and title_h1.get_text(strip=True):
        spell_data['Name'] = title_h1.get_text(strip=True)
    
    for child in main_content.children:
        if isinstance(child, str):
            text = child.strip()
            if text and len(text) > 2 and 'Name' not in spell_data:
                spell_data['Name'] = text
        elif child.name == 'span':
            span_text = child.get_text(strip=True)
            if span_text.startswith('Spell ') or span_text.startswith('Cantrip ') or span_text.startswith('Focus '):
                if 'Level' not in spell_data:
                    spell_data['Level'] = span_text.replace('Spell', '').replace('Cantrip', '').replace('Focus', '').strip()
            if child.get('aria-label') and 'Actions' not in spell_data:
                if 'Action' in child.get('aria-label') or 'Reaction' in child.get('aria-label') or 'Free' in child.get('aria-label'):
                    spell_data['Actions'] = child.get('aria-label')
            
    # 2. Traits
    traits = []
    for trait_span in main_content.find_all('span', class_=re.compile(r'trait.*')):
        # AoN has traits in spans with classes like "trait", "traituncommon", etc.
        text = trait_span.get_text(strip=True)
        if text: traits.append(text)
    if traits:
        spell_data['Traits'] = list(dict.fromkeys(traits)) # Remove duplicates
        
    # 3. Metadata fields
    for b_tag in main_content.find_all('b'):
        key = b_tag.get_text(strip=True)
        if key in ['Source', 'Traditions', 'Cast', 'Range', 'Area', 'Saving Throw', 'Duration', 'Targets', 'Bloodline', 'Deities']:
            value_parts = []
            sibling = b_tag.next_sibling
            while sibling:
                if sibling.name in ['br', 'hr', 'b']:
                    break
                if isinstance(sibling, str):
                    value_parts.append(sibling.strip())
                else:
                    value_parts.append(sibling.get_text(strip=True))
                sibling = sibling.next_sibling
                
            value = ' '.join(p for p in value_parts if p).strip()
            if value.startswith(';'): value = value[1:].strip()
            
            spell_data[key] = value

    # 4. Description
    target_hr = None
    for hr in main_content.find_all('hr'):
        classes = hr.get('class', [])
        if not classes or 'hide-on-print' not in classes:
            target_hr = hr
            break
            
    if target_hr:
        desc_parts = []
        sibling = target_hr.next_sibling
        while sibling:
            if sibling.name in ['h2', 'hr']: # Stop at Heightened or next hr
                break
            if isinstance(sibling, str):
                text = sibling.strip()
                if text: desc_parts.append(text)
            elif sibling.name != 'br':
                text = sibling.get_text(strip=True)
                if text: desc_parts.append(text)
            sibling = sibling.next_sibling
            
        description = '\n'.join(desc_parts).strip()
        if description:
            spell_data['Description'] = description
            
    return spell_data
