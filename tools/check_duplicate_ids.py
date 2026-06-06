"""Check output JSON files for duplicate top-level ``id`` values.

The scrape pipeline writes an array of records, each with a derived ``id``
(see ``_derive_spell_id`` in ``rpg_parser/adapters/parsers/pf2e_aon.py``).
Because ids come from names, two records can collide on the same ``id``.
This tool reports any duplicate ids (empty-string ids included) and exits
non-zero when duplicates are found, so it can be used ad-hoc or in CI.

Usage:
    python tools/check_duplicate_ids.py FILE [FILE ...]

Exit codes:
    0  no duplicates in any file
    1  duplicates found
    2  usage / IO / JSON / structure error
"""

import argparse
import json
import sys

MISSING_ID = "<missing>"


def find_duplicate_ids(records: list) -> dict:
    """Return ``{id: [indices...]}`` for every id seen in 2+ records.

    Records without an ``id`` key are grouped under ``MISSING_ID``. Empty
    strings are treated like any other value, so multiple empty ids are
    reported as duplicates.
    """
    seen: dict = {}
    for index, record in enumerate(records):
        if "id" in record:
            key = record["id"]
        else:
            key = MISSING_ID
        seen.setdefault(key, []).append(index)
    return {key: indices for key, indices in seen.items() if len(indices) > 1}


def load_records(path: str) -> list:
    """Load a JSON file and normalize it to a list of record dicts.

    A single object (fetch output) becomes a one-element list. Raises
    ``ValueError`` for unexpected shapes or non-dict entries.
    """
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(f"expected a JSON object or array, got {type(data).__name__}")

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"entry at index {index} is {type(record).__name__}, not an object")

    return records


def _label(id_value) -> str:
    if id_value == MISSING_ID:
        return "(missing id)"
    if id_value == "":
        return "(empty id)"
    return repr(id_value)


def check_file(path: str) -> int:
    """Check one file. Return 0 (clean), 1 (duplicates), or 2 (error)."""
    try:
        records = load_records(path)
    except FileNotFoundError:
        print(f"{path}: ERROR file not found")
        return 2
    except json.JSONDecodeError as e:
        print(f"{path}: ERROR invalid JSON ({e})")
        return 2
    except (OSError, ValueError) as e:
        print(f"{path}: ERROR {e}")
        return 2

    duplicates = find_duplicate_ids(records)
    if not duplicates:
        print(f"{path}: OK ({len(records)} records, no duplicate ids)")
        return 0

    print(f"{path}: FAIL ({len(records)} records, {len(duplicates)} duplicate id(s))")
    for id_value, indices in sorted(duplicates.items(), key=lambda kv: str(kv[0])):
        names = [records[i].get("Name", "?") for i in indices]
        pairs = ", ".join(f"index {i} (Name={n!r})" for i, n in zip(indices, names))
        print(f"  {_label(id_value)}: {pairs}")
    return 1


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check output JSON files for duplicate top-level 'id' values.",
    )
    parser.add_argument("files", nargs="+", help="Output JSON file(s) to check.")
    args = parser.parse_args(argv)

    worst = 0
    for path in args.files:
        result = check_file(path)
        worst = max(worst, result)
    return worst


if __name__ == "__main__":
    sys.exit(main())
