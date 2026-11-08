"""Пути, типы столбцов и параметры команд базы данных."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
JSON_ENCODING = "utf-8"
JSON_INDENT = 4
TEMP_NAME_BYTES = 16
SAFE_FILENAME_BYTES = b"abcdefghijklmnopqrstuvwxyz0123456789_.-~"

ID_COLUMN = "ID"
ID_TYPE = "int"
COLUMN_TYPES = {"int": int, "str": str, "bool": bool}

COMMAND_PROMPT = "Введите команду: "
CONFIRM_ANSWER = "y"
INVALID_VALUE = "Некорректное значение: {}. Попробуйте снова."
TABLE_COMMANDS = {"create_table", "drop_table", "list_tables", "help", "exit"}
DATA_COMMANDS = {"insert", "select", "update", "delete", "info"}
