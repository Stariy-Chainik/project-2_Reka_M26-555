import json
from pathlib import Path
from tempfile import TemporaryDirectory


def load_metadata(filepath):
    try:
        with Path(filepath).open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    path = Path(filepath)
    with TemporaryDirectory(dir=path.parent) as directory:
        temporary_path = Path(directory) / path.name
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        temporary_path.replace(path)
