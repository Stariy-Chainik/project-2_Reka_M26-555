import shlex

import prompt

from primitive_db.core import INVALID_VALUE, create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

HELP = """***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> exit - выход из программы
<command> help - справочная информация"""


def print_help() -> None:
    print(HELP)


def _save_changes(filepath, metadata) -> bool:
    try:
        save_metadata(filepath, metadata)
    except OSError as error:
        print(f"Ошибка сохранения метаданных: {error}")
        return False
    return True


def run(filepath="db_meta.json") -> None:
    print_help()

    while True:
        try:
            user_input = prompt.string("Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            return

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(INVALID_VALUE.format(user_input))
            continue

        match args:
            case []:
                continue
            case ["exit"]:
                return
            case ["help"]:
                print_help()
                continue
            case ["list_tables"] | ["drop_table", _] | ["create_table", _, _, *_]:
                pass
            case [command, *values] if command in {
                "create_table", "drop_table", "list_tables", "help", "exit"
            }:
                print(INVALID_VALUE.format(" ".join(values) or command))
                continue
            case [command, *_]:
                print(f"Функции {command} нет. Попробуйте снова.")
                continue

        try:
            metadata = load_metadata(filepath)
        except (OSError, ValueError) as error:
            print(f"Ошибка чтения метаданных: {error}")
            continue
        if not isinstance(metadata, dict):
            print("Ошибка чтения метаданных: ожидался JSON-объект.")
            continue

        table_count = len(metadata)
        match args:
            case ["list_tables"]:
                if not metadata:
                    print("Таблиц пока нет.")
                for table_name in metadata:
                    print(f"- {table_name}")
            case ["create_table", table_name, *columns]:
                metadata = create_table(metadata, table_name, columns)
                if len(metadata) != table_count and _save_changes(filepath, metadata):
                    column_list = ", ".join(metadata[table_name])
                    print(
                        f'Таблица "{table_name}" успешно создана со столбцами: '
                        f"{column_list}"
                    )
            case ["drop_table", table_name]:
                metadata = drop_table(metadata, table_name)
                if len(metadata) != table_count and _save_changes(filepath, metadata):
                    print(f'Таблица "{table_name}" успешно удалена.')
