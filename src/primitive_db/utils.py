import json
import os

from primitive_db.constants import (
    DATA_DIR,
    JSON_ENCODING,
    JSON_INDENT,
    SAFE_FILENAME_BYTES,
    TEMP_NAME_BYTES,
)


def _load_json(filepath, default):
    """Прочитать JSON или вернуть значение по умолчанию при отсутствии файла."""
    try:
        with open(filepath, encoding=JSON_ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _save_json(filepath, data):
    """Записать JSON во временный файл и атомарно заменить исходный."""
    directory = os.path.dirname(filepath)
    temporary_path = os.path.join(
        directory, f".db-{os.urandom(TEMP_NAME_BYTES).hex()}.tmp"
    )
    file = open(temporary_path, "x", encoding=JSON_ENCODING)
    try:
        with file:
            json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)
        os.replace(temporary_path, filepath)
    finally:
        try:
            os.remove(temporary_path)
        except FileNotFoundError:
            pass


def load_metadata(filepath):
    """Загрузить схемы таблиц из JSON."""
    return _load_json(filepath, {})


def save_metadata(filepath, data):
    """Сохранить схемы таблиц в JSON."""
    _save_json(filepath, data)


def _table_path(table_name, data_dir):
    """Сохранить разные имена таблиц в разных файлах, включая регистр букв."""
    filename = "".join(
        chr(byte) if byte in SAFE_FILENAME_BYTES else f"%{byte:02X}"
        for byte in table_name.encode(JSON_ENCODING)
    )
    return os.path.join(data_dir, f"{filename}.json")


def load_table_data(table_name, data_dir=DATA_DIR):
    """Загрузить строки таблицы из её JSON-файла."""
    rows = _load_json(_table_path(table_name, data_dir), [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'Данные таблицы "{table_name}" должны быть списком записей.')
    return rows


def save_table_data(table_name, data, data_dir=DATA_DIR):
    """Сохранить строки таблицы в её JSON-файл."""
    path = _table_path(table_name, data_dir)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    _save_json(path, data)


def remove_table_data(table_name, data_dir=DATA_DIR):
    """Удалить файл строк таблицы, если он существует."""
    try:
        os.remove(_table_path(table_name, data_dir))
    except FileNotFoundError:
        pass
