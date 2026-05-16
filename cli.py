import argparse
import re
from scraper import fetch_spell_html
from parser import parse_aon_spell
from exporter import save_as_json

def create_valid_filename(spell_name: str) -> str:
    """Generates a valid filename from the spell name."""
    name = re.sub(r'[^\w\-_\. ]', '_', spell_name)
    name = name.replace(' ', '_').lower()
    if not name:
        name = "downloaded_spell"
    return f"{name}.json"

def main():
    parser = argparse.ArgumentParser(description="AoN Spell Parser: Download and convert Pathfinder 2e spells to JSON.")
    parser.add_argument("url", help="The URL of the Archives of Nethys spell page.")
    parser.add_argument("-o", "--output", help="Optional output filename.")
    
    args = parser.parse_args()
    
    print(f"Fetching {args.url}...")
    try:
        html = fetch_spell_html(args.url)
        print("Extracting spell data...")
        spell_data = parse_aon_spell(html)
        
        # Determine filename
        if args.output:
            output_filename = args.output
        elif 'Name' in spell_data:
            output_filename = create_valid_filename(spell_data['Name'])
        else:
            output_filename = "spell.json"
            
        print(f"Saving to {output_filename}...")
        save_as_json(spell_data, output_filename)
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
