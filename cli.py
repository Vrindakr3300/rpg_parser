import argparse
import re

from rpg_parser.core.pipeline import run_pipeline
from rpg_parser.core.ports import ExportTarget, FetchRequest
from rpg_parser.registry import get_pipeline

def create_valid_filename(spell_name: str) -> str:
    """Generates a valid filename from the spell name."""
    name = re.sub(r'[^\w\-_\. ]', '_', spell_name)
    name = name.replace(' ', '_').lower()
    if not name:
        name = "downloaded_spell"
    return f"{name}.json"

def main():
    parser = argparse.ArgumentParser(description="RPG Parser: Download and convert RPG data to JSON.")
    parser.add_argument("url", help="The URL or source location to fetch.")
    parser.add_argument("-o", "--output", help="Optional output filename.")
    parser.add_argument("--system", default="pf2e", help="RPG system to parse. Defaults to pf2e.")
    parser.add_argument("--type", default="spell", dest="content_type", help="Content type to parse. Defaults to spell.")
    parser.add_argument("--source", default="aon-html", help="Source adapter to use. Defaults to aon-html.")
    
    args = parser.parse_args()
    
    print(f"Fetching {args.url}...")
    try:
        pipeline = get_pipeline(args.system, args.content_type, args.source)
        print("Extracting data...")
        spell_data = run_pipeline(pipeline, FetchRequest(location=args.url))
        
        # Determine filename
        if args.output:
            output_filename = args.output
        elif 'Name' in spell_data:
            output_filename = create_valid_filename(spell_data['Name'])
        else:
            output_filename = "spell.json"
            
        print(f"Saving to {output_filename}...")
        pipeline.exporter.export(spell_data, ExportTarget(location=output_filename))
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
