# Attribution & Data Notices

This project is an **unofficial, fan-made** utility. It is not affiliated with,
endorsed by, or sponsored by Paizo Inc. or Archives of Nethys.

## Source of the data

Any spell data this tool produces — and the sample fixtures committed in this
repository — derive from content published on
[Archives of Nethys](https://aonprd.com/), the official online reference for
Pathfinder. That content is owned by **Paizo Inc.**

The repository ships a few small files under `samples/` (`*.html` source-page
fixtures and `*.json` example outputs). These are included **only** as test
fixtures and documentation examples for the parser, not as a redistributable
dataset. The bulk spell datasets that were previously committed have been
removed; generate your own data with the CLI instead.

## Licensing of the game data

The game data is open content, licensed by Paizo depending on the system:

- **Pathfinder 1e** — [Open Game License (OGL)](https://opengamingfoundation.org/ogl.html)
- **Pathfinder 2e** — [Open RPG Creative (ORC) License](https://paizo.com/orclicense)

If you use, distribute, or publish data obtained with this tool, **you** are
responsible for complying with the applicable license, including its attribution
requirements (OGL Section 15 / the ORC attribution notice), which carry over to
any redistributed output. The code of this tool is separately licensed under the
[MIT License](LICENSE).

## Trademarks

"Pathfinder", "Archives of Nethys", and related names, logos, and marks are the
property of their respective owners and are referenced here for identification
purposes only.

## Responsible scraping

Archives of Nethys is a community resource. Please be considerate: use a
conservative request `--delay`, keep `--workers` low, and avoid repeated large
scrapes. This tool sends a descriptive `User-Agent` identifying itself; please
do not change it to impersonate a web browser.
