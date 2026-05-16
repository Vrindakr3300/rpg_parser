import json
import os

def save_as_json(data: dict, filename: str):
    """Saves a python dictionary as a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
