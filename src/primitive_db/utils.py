import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote


def _load_json(filepath, default):
    try:
        with Path(filepath).open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _save_json(filepath, data):
    path = Path(filepath)
    with TemporaryDirectory(dir=path.parent) as directory:
        temporary_path = Path(directory) / path.name
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        temporary_path.replace(path)


def load_metadata(filepath):
    return _load_json(filepath, {})


def save_metadata(filepath, data):
    _save_json(filepath, data)


def _table_path(table_name, data_dir):
    # Encode uppercase letters as well to keep distinct names distinct on macOS.
    filename = "".join(
        f"%{ord(char):02X}" if "A" <= char <= "Z" else quote(char, safe="")
        for char in table_name
    )
    return Path(data_dir) / f"{filename}.json"


def load_table_data(table_name, data_dir="data"):
    rows = _load_json(_table_path(table_name, data_dir), [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'Данные таблицы "{table_name}" должны быть списком записей.')
    return rows


def save_table_data(table_name, data, data_dir="data"):
    path = _table_path(table_name, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(path, data)


def remove_table_data(table_name, data_dir="data"):
    _table_path(table_name, data_dir).unlink(missing_ok=True)
