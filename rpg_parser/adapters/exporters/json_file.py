import json
from typing import Any

from rpg_parser.core.ports import ExportTarget


class JsonFileExporter:
    """Exports structured data to a JSON file."""

    def export(self, data: dict[str, Any], target: ExportTarget) -> None:
        with open(target.location, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
