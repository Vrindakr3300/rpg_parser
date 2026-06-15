# Attribution & Data Notices

This project is an **unofficial, fan-made** utility. It is not affiliated with,
endorsed by, or sponsored by Paizo Inc., Archives of Nethys, Wizards of the
Coast, or Open5e.

## Source of the data

Pathfinder spell data this tool produces — and the Pathfinder sample fixtures
committed in this repository — derive from content published on
[Archives of Nethys](https://aonprd.com/), the official online reference for
Pathfinder. That content is owned by **Paizo Inc.**

D&D 5e spell data is fetched from the [Open5e](https://open5e.com/) API, which
serves the **D&D 5e System Reference Document (SRD)** published by **Wizards of
the Coast LLC**. The committed `samples/sample_dnd5e_open5e_*.json` fixtures are
small excerpts of that SRD data, included only as parser/scraper test fixtures.

The repository ships a few small files under `samples/` (`*.html` source-page
fixtures and `*.json` example outputs). These are included **only** as test
fixtures and documentation examples for the parser, not as a redistributable
dataset. The bulk spell datasets that were previously committed have been
removed; generate your own data with the CLI instead.

## Licensing of the game data

The game data is open content, licensed depending on the system:

- **Pathfinder 1e** — [Open Game License (OGL)](https://opengamingfoundation.org/ogl.html)
- **Pathfinder 2e** — [Open RPG Creative (ORC) License](https://paizo.com/orclicense)
- **D&D 5e SRD** — [Creative Commons Attribution 4.0 (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/)

If you use, distribute, or publish data obtained with this tool, **you** are
responsible for complying with the applicable license, including its attribution
requirements (OGL Section 15 / the ORC attribution notice / the CC-BY-4.0
attribution), which carry over to any redistributed output. The code of this
tool is separately licensed under the [MIT License](LICENSE).

For D&D 5e data, CC-BY-4.0 requires an attribution notice such as:

> This work includes material from the System Reference Document 5.2 ("SRD 5.2")
> by Wizards of the Coast LLC, available under the Creative Commons Attribution
> 4.0 International License (https://creativecommons.org/licenses/by/4.0/).

Every `dnd5e` record this tool emits already carries that attribution in its
`Source` field — preserve it when redistributing.

## Trademarks

"Pathfinder", "Archives of Nethys", "Dungeons & Dragons", "D&D", and related
names, logos, and marks are the property of their respective owners and are
referenced here for identification purposes only.

## Responsible scraping

Archives of Nethys and Open5e are community resources. Please be considerate:
use a conservative request `--delay`, keep `--workers` low, and avoid repeated
large scrapes. This tool sends a descriptive `User-Agent` identifying itself;
please do not change it to impersonate a web browser.
