import argparse
import re
import sys

from rpg_parser.core.pipeline import run_pipeline, run_scrape_pipeline
from rpg_parser.core.ports import ExportTarget, FetchRequest, ScrapeRequest
from rpg_parser.registry import default_source, get_pipeline, get_scrape_pipeline


def create_valid_filename(spell_name: str) -> str:
    """Generates a valid filename from the spell name."""
    name = re.sub(r'[^\w\-_\. ]', '_', spell_name)
    name = name.replace(' ', '_').lower()
    if not name:
        name = "downloaded_spell"
    return f"{name}.json"

def add_pipeline_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--system", default="pf2e", help="RPG system to parse. Defaults to pf2e.")
    parser.add_argument("--type", default="spell", dest="content_type", help="Content type to parse. Defaults to spell.")
    parser.add_argument("--source", default=None, help="Source adapter to use. Defaults to aon-html (open5e for dnd5e).")


def resolve_source(args: argparse.Namespace) -> None:
    if args.source is None:
        args.source = default_source(args.system)


def build_fetch_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RPG Parser: Download and convert one RPG record to JSON.")
    parser.add_argument("url", help="The URL or source location to fetch.")
    parser.add_argument("-o", "--output", help="Optional output filename.")
    add_pipeline_args(parser)
    return parser


def build_scrape_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RPG Parser: Scrape many RPG records to JSON files.")
    parser.add_argument("--location", help="Optional source root location for discovery.")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum records to discover. Defaults to 5000.")
    parser.add_argument("--tradition", help="PF2e spell tradition filter for AoN discovery.")
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between starting detail-page requests. Defaults to 1.0.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Maximum concurrent detail-page requests. Defaults to 1.",
    )
    parser.add_argument("-o", "--output", default="scraped.json", help="Output JSON file for scraped records.")
    add_pipeline_args(parser)
    return parser


def run_fetch(args: argparse.Namespace) -> None:
    resolve_source(args)
    print(f"Fetching {args.url}...")
    pipeline = get_pipeline(args.system, args.content_type, args.source)
    print("Extracting data...")
    spell_data = run_pipeline(pipeline, FetchRequest(location=args.url))

    if args.output:
        output_filename = args.output
    elif 'Name' in spell_data:
        output_filename = create_valid_filename(spell_data['Name'])
    else:
        output_filename = "spell.json"

    print(f"Saving to {output_filename}...")
    pipeline.exporter.export(spell_data, ExportTarget(location=output_filename))
    print("Done!")


def run_scrape(args: argparse.Namespace) -> None:
    resolve_source(args)
    filters = {}
    if args.tradition:
        filters["tradition"] = args.tradition

    pipeline = get_scrape_pipeline(args.system, args.content_type, args.source)
    print(f"Scraping {args.system}/{args.content_type}/{args.source}...")

    records = run_scrape_pipeline(
        pipeline,
        ScrapeRequest(location=args.location, filters=filters, limit=args.limit),
        delay_seconds=args.delay,
        max_workers=args.workers,
    )

    print(f"Saving {len(records)} records to {args.output}...")
    pipeline.exporter.export(records, ExportTarget(location=args.output))
    print(f"Done! Exported {len(records)} records to {args.output}.")


def main(argv: list[str] | None = None):
    argv = list(sys.argv[1:] if argv is None else argv)

    try:
        if argv and argv[0] == "scrape":
            args = build_scrape_parser().parse_args(argv[1:])
            run_scrape(args)
        elif argv and argv[0] == "fetch":
            args = build_fetch_parser().parse_args(argv[1:])
            run_fetch(args)
        else:
            args = build_fetch_parser().parse_args(argv)
            run_fetch(args)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
