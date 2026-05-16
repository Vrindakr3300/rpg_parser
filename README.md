# RPG Parser

Command-line utility for fetching Pathfinder 2e spell data from Archives of Nethys and exporting structured JSON.

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

Write a single spell to a specific JSON file:

```bash
uv run python cli.py fetch "https://2e.aonprd.com/Spells.aspx?ID=1528" -o spell.json
```

Scrape multiple spells discovered through AoN Elasticsearch:

```bash
uv run python cli.py scrape --limit 10 --tradition arcane -o scraped
```

The default pipeline options are `--system pf2e --type spell --source aon-html`.

## Testing

Run all tests:

```bash
uv run python -m unittest discover -s tests
```

Run the offline unit tests:

```bash
uv run python -m unittest tests.test_pipeline tests.test_registry tests.test_aon_scraper tests.test_scrape_pipeline
```

Run the live AoN integration test:

```bash
uv run python -m unittest tests.test_scraper.TestScraperIntegration.test_fetch_fireball
```
