# RPG Parser

Command-line utility for fetching Pathfinder 1e and 2e spell data from Archives of Nethys and exporting structured JSON.

## Features

- **Multi-System Support**: Extract spell data for both Pathfinder 2e and Pathfinder 1e.
- **Single & Bulk Fetching**: Fetch individual spells from a URL, or discover and scrape hundreds of spells using AoN's Elasticsearch API.
- **Polite Scraping**: Built-in concurrency controls and configurable delays to respect server load.
- **Structured Output**: Exports cleaned, structured data as JSON files.

## Prerequisites

- **Python 3.14+**
- **[uv](https://github.com/astral-sh/uv)** for fast Python environment and dependency management.

## Setup

```bash
uv sync
```

## CLI Usage

Fetch one spell from an AoN detail page:

```bash
uv run python cli.py "https://2e.aonprd.com/Spells.aspx?ID=1528"
```

The explicit `fetch` subcommand is equivalent:

```bash
uv run python cli.py fetch "https://2e.aonprd.com/Spells.aspx?ID=1528"
```

Fetch a Pathfinder 1e spell by specifying the `--system`:

```bash
uv run python cli.py fetch "https://aonprd.com/SpellDisplay.aspx?ItemName=Magic Missile" --system pf1e
```

Write a single spell to a specific JSON file:

```bash
uv run python cli.py fetch "https://2e.aonprd.com/Spells.aspx?ID=1528" -o spell.json
```

Scrape multiple spells discovered through AoN Elasticsearch into a single JSON array file (default `scraped.json`):

```bash
uv run python cli.py scrape --limit 10 --tradition arcane -o scraped.json
```

For larger scrapes, increase concurrency and reduce the delay between detail-page requests:

```bash
uv run python cli.py scrape --tradition arcane --workers 4 --delay 0.25 -o scraped.json
```

The scrape defaults are conservative: `--workers 1 --delay 1.0`.

The default pipeline options are `--system pf2e --type spell --source aon-html`.

## Output Example

When exporting a spell, the tool generates structured JSON preserving the original content's schema as closely as possible. Here is a brief example of the expected output format:

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

## Architecture

This project uses a modular "Ports and Adapters" (Hexagonal) architecture located in the `rpg_parser/` package. This makes it highly extensible:
- **Core Logic (`rpg_parser/core/`)**: Protocols defining the interfaces for `Fetcher`, `Parser`, `Exporter`, and `Scraper`. Orchestrates the pipeline.
- **Adapters (`rpg_parser/adapters/`)**: Concrete implementations for fetching data (e.g., HTML requests), parsing DOM elements (using BeautifulSoup), and exporting files (JSON).
- **Registry (`rpg_parser/registry.py`)**: A centralized mapping of systems and content types, allowing you to easily add new supported systems (e.g., Starfinder) or object types (e.g., feats, items) without rewriting CLI logic.

## Testing

Run all tests:

```bash
uv run python -m unittest discover -s tests
```

Run the offline unit tests:

```bash
uv run python -m unittest tests.test_pipeline tests.test_registry tests.test_aon_scraper tests.test_scrape_pipeline tests.test_pf1e_parser
```

Run the live AoN integration test:

```bash
uv run python -m unittest tests.test_scraper.TestScraperIntegration.test_fetch_fireball
```

## Contributing

This is a public open-source project on GitHub. Contributions, bug reports, and pull requests are welcome!

## License and Legal

**Code License:** The code for this utility is released under the [MIT License](LICENSE).

**Data License:** The data downloaded and parsed by this tool originates from the [Archives of Nethys](https://aonprd.com/). The licensing for this data depends on the system being parsed:
- **Pathfinder 1e** data is governed by the [Open Game License (OGL)](https://opengamingfoundation.org/ogl.html).
- **Pathfinder 2e** data is governed by the [Open RPG Creative (ORC) License](https://paizo.com/orclicense).

When using, distributing, or publishing data scraped with this tool, you must comply with the respective license (OGL or ORC) and any other applicable policies specified by Paizo Inc. and Archives of Nethys.
