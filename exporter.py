from rpg_parser.adapters.exporters.json_file import JsonFileExporter
from rpg_parser.core.ports import ExportTarget


def save_as_json(data: dict, filename: str):
    """Saves a python dictionary as a JSON file."""
    JsonFileExporter().export(data, ExportTarget(location=filename))
