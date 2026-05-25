# RPG Parser

Command-line utility for fetching Pathfinder 1e and Pathfinder 2e spell data from Archives of Nethys and exporting structured JSON.

## What It Does

- Fetches a single spell from an Archives of Nethys detail page.
- Scrapes many spells into one JSON array file.
- Supports Pathfinder 1e and Pathfinder 2e spell pages.
- Uses conservative scraping defaults with configurable concurrency and delay.
- Keeps fetch, parse, scrape, and export logic separated so new systems and sources can be added without rewriting the CLI.

## Supported Pipelines

| System | Content Type | Source | Fetch | Scrape |
| --- | --- | --- | --- | --- |
| `pf2e` | `spell` | `aon-html` | yes | yes |
| `pf1e` | `spell` | `aon-html` | yes | yes |

The default pipeline options are `--system pf2e --type spell --source aon-html`.

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) for environment and dependency management

## Installation

```bash
uv sync
```

## Quick Start

Fetch one Pathfinder 2e spell from an AoN detail page:

```bash
uv run python cli.py "https://2e.aonprd.com/Spells.aspx?ID=1528"
```

Fetch one Pathfinder 1e spell:

```bash
uv run python cli.py fetch "https://aonprd.com/SpellDisplay.aspx?ItemName=Magic Missile" --system pf1e
```

Scrape the first 10 PF2e arcane spells into `scraped.json`:

```bash
uv run python cli.py scrape --limit 10 --tradition arcane -o scraped.json
```

Scrape PF1e spells:

```bash
uv run python cli.py scrape --system pf1e --limit 10 -o pf1e_spells.json
```

## CLI Usage

### Fetch

`fetch` downloads one detail page, parses it, and writes one JSON file.

```bash
uv run python cli.py fetch <AoN-spell-url> [options]
```

The `fetch` subcommand is optional. This is equivalent:

```bash
uv run python cli.py <AoN-spell-url> [options]
```

Common fetch options:

| Option | Default | Description |
| --- | --- | --- |
| `-o, --output` | generated from spell name | Output JSON file. |
| `--system` | `pf2e` | RPG system to parse. |
| `--type` | `spell` | Content type to parse. |
| `--source` | `aon-html` | Source adapter to use. |

Examples:

```bash
uv run python cli.py fetch "https://2e.aonprd.com/Spells.aspx?ID=1528" -o spell.json
uv run python cli.py fetch "https://aonprd.com/SpellDisplay.aspx?ItemName=Fireball" --system pf1e
```

If `--output` is omitted, the filename is generated from the parsed spell name. Invalid filename characters become `_`, spaces become `_`, and names are lowercased.

### Scrape

`scrape` discovers many detail pages, fetches each page, parses each spell, and writes one JSON array file.

```bash
uv run python cli.py scrape [options]
```

Common scrape options:

| Option | Default | Description |
| --- | --- | --- |
| `-o, --output` | `scraped.json` | Output JSON array file. |
| `--limit` | `5000` | Maximum records to discover. |
| `--tradition` | none | PF2e spell tradition filter for AoN discovery. |
| `--workers` | `1` | Maximum concurrent detail-page requests. |
| `--delay` | `1.0` | Seconds to wait between starting detail-page requests. |
| `--location` | none | Optional source root location for discovery. |
| `--system` | `pf2e` | RPG system to parse. |
| `--type` | `spell` | Content type to parse. |
| `--source` | `aon-html` | Source adapter to use. |

For larger scrapes, increase concurrency cautiously:

```bash
uv run python cli.py scrape --tradition arcane --workers 4 --delay 0.25 -o scraped.json
```

PF2e scrape discovery uses the AoN Elasticsearch endpoint. PF1e scrape discovery parses `https://aonprd.com/Spells.aspx?Class=All` for spell detail links.

## Output

JSON output uses 4-space indentation and preserves non-ASCII characters.

Example PF2e HTML output:

```json
{
    "Name": "Fireball",
    "Source": "Player Core pg. 330",
    "Traditions": "Arcane, Primal",
    "Cast": "2",
    "Range": "500 feet",
    "Area": "20-foot burst",
    "Saving Throw": "basic Reflex",
    "Description": "A roaring blast of fire appears at a spot you designate, dealing 6d6 fire damage.",
    "url": "https://2e.aonprd.com/Spells.aspx?ID=1524"
}
```

The HTML parser output preserves source-page field names where practical, such as `Name`, `Traits`, `Traditions`, and `Description`.

## Architecture

The project uses a small ports-and-adapters shape under `rpg_parser/`.

| Area | Path | Responsibility |
| --- | --- | --- |
| Core ports | `rpg_parser/core/ports.py` | Protocols for fetchers, parsers, scrapers, and exporters. |
| Orchestration | `rpg_parser/core/pipeline.py` | Runs fetch and scrape pipelines. |
| Adapters | `rpg_parser/adapters/` | AoN fetchers, parsers, scrapers, and JSON export. |
| Registry | `rpg_parser/registry.py` | Maps `system/type/source` combinations to pipeline implementations. |
| CLI | `cli.py` | Parses command-line arguments and invokes registered pipelines. |

To add a new RPG system, content type, or source, add the relevant adapter implementations and register them in `rpg_parser/registry.py`. Avoid wiring source-specific parser or scraper behavior directly into `cli.py`.

## Testing

Run all tests:

```bash
uv run python -m unittest discover -s tests
```

Run focused offline tests:

```bash
uv run python -m unittest tests.test_pipeline tests.test_registry tests.test_aon_scraper tests.test_scrape_pipeline tests.test_pf1e_scraper tests.test_pf2e_aon_parser tests.test_pf1e_parser
```

Run the live AoN integration test:

```bash
uv run python -m unittest tests.test_scraper.TestScraperIntegration.test_fetch_fireball
```

The live integration test requires network access and can fail if Archives of Nethys changes its API or page markup.

## Troubleshooting

- `Unsupported pipeline`: check `--system`, `--type`, and `--source` against the supported pipeline table.
- Empty or failed scrape results: try a smaller `--limit`, slower `--delay`, or verify AoN is reachable.
- Parser errors: AoN detail-page markup may have changed; compare parser behavior against files in `samples/`.

## Contributing

Contributions, bug reports, and pull requests are welcome.

When changing parser behavior, validate against the sample HTML fixtures and add or update tests for the affected system.

## License and Legal

**Code License:** The code for this utility is released under the [MIT License](LICENSE).

**Data License:** The data downloaded and parsed by this tool originates from [Archives of Nethys](https://aonprd.com/). The licensing for this data depends on the system being parsed:

- Pathfinder 1e data is governed by the [Open Game License (OGL)](https://opengamingfoundation.org/ogl.html).
- Pathfinder 2e data is governed by the [Open RPG Creative (ORC) License](https://paizo.com/orclicense).

When using, distributing, or publishing data scraped with this tool, you must comply with the respective license and any other applicable policies specified by Paizo Inc. and Archives of Nethys.
