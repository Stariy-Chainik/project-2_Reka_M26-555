import os
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    COMMAND_PROMPT,
    DATA_COMMANDS,
    DATA_DIR,
    ID_COLUMN,
    INVALID_VALUE,
    META_FILE,
    TABLE_COMMANDS,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    matching_rows,
    select,
    table_schema,
    update,
    validate_values,
)
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import parse_data_command
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)

HELP = """***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***
<command> insert into <таблица> values (<значение1>, <значение2>, ...)
<command> select from <таблица> [where <столбец> = <значение>]
<command> update <таблица> set <столбец> = <значение> where <столбец> = <значение>
<command> delete from <таблица> where <столбец> = <значение>
<command> info <таблица> - показать схему и количество записей

<command> exit - выход из программы
<command> help - справочная информация"""


def print_help() -> None:
    """Показать список доступных команд."""
    print(HELP)


@handle_db_errors
def _run_table_command(args, metadata, filepath, data_dir):
    """Обработать команду создания, просмотра или удаления таблиц."""
    table_count = len(metadata)
    match args:
        case ["list_tables"]:
            if not metadata:
                print("Таблиц пока нет.")
            for table_name in metadata:
                print(f"- {table_name}")
        case ["create_table", table_name, *columns]:
            metadata = create_table(metadata, table_name, columns)
            if metadata is not None and len(metadata) != table_count:
                save_table_data(table_name, [], data_dir)
                save_metadata(filepath, metadata)
                column_list = ", ".join(metadata[table_name])
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: '
                    f"{column_list}"
                )
        case ["drop_table", table_name]:
            metadata = drop_table(metadata, table_name)
            if metadata is not None and len(metadata) != table_count:
                save_metadata(filepath, metadata)
                remove_table_data(table_name, data_dir)
                print(f'Таблица "{table_name}" успешно удалена.')


@handle_db_errors
def _run_data_command(args, metadata, data_dir, select_caches):
    """Выполнить команду над строками и сохранить успешные изменения."""
    _, table_name, *_ = args
    schema = table_schema(metadata, table_name)
    if schema is None:
        return
    rows = load_table_data(table_name, data_dir)
    for row in rows:
        if row.keys() != schema.keys():
            raise ValueError(f'Запись в таблице "{table_name}" не соответствует схеме.')
        if not validate_values(schema, row):
            return

    match args:
        case ["info", _]:
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {', '.join(metadata[table_name])}")
            print(f"Количество записей: {len(rows)}")
            return
        case ["select", _, condition]:
            if condition is not None and not validate_values(schema, condition):
                return
            snapshot = (schema, rows)
            previous, cache_result = select_caches.get(table_name, (None, None))
            if snapshot != previous:
                cache_result = create_cacher()
                select_caches[table_name] = snapshot, cache_result
            selected = select(rows, condition, cache_result=cache_result)
            if selected is None:
                return
            table = PrettyTable(list(schema))
            table.add_rows([[row[column] for column in schema] for row in selected])
            print(table)
            return
        case ["insert", _, values]:
            updated = insert(metadata, table_name, values, table_data=rows)
            if updated is None:
                return
            affected = updated[-1:]
            message = 'успешно добавлена в таблицу "{table_name}".'
        case ["update", _, changes, condition]:
            if not validate_values(schema, changes) or not validate_values(
                schema, condition
            ):
                return
            affected = matching_rows(rows, condition)
            updated = update(rows, changes, condition)
            message = 'в таблице "{table_name}" успешно обновлена.'
        case ["delete", _, condition]:
            if not validate_values(schema, condition):
                return
            affected = matching_rows(rows, condition)
            updated = delete(rows, condition)
            message = 'успешно удалена из таблицы "{table_name}".'

    if updated is None:
        return
    if not affected:
        print("Подходящих записей нет.")
        return
    save_table_data(table_name, updated, data_dir)
    for row in affected:
        print(f"Запись с ID={row[ID_COLUMN]} {message.format(table_name=table_name)}")


def run(filepath=META_FILE) -> None:
    """Читать команды и вызывать их обработчики до выхода из программы."""
    data_dir = os.path.join(os.path.dirname(filepath), DATA_DIR)
    select_caches = {}
    print_help()

    while True:
        try:
            user_input = prompt.string(COMMAND_PROMPT)
        except (EOFError, KeyboardInterrupt):
            return

        words = user_input.split(maxsplit=1)
        if not words:
            continue
        is_data_command = words[0] in DATA_COMMANDS
        try:
            args = (
                parse_data_command(user_input)
                if is_data_command
                else shlex.split(user_input)
            )
        except ValueError as error:
            value = str(error) if is_data_command else user_input
            print(INVALID_VALUE.format(value or user_input))
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
            case _ if is_data_command:
                pass
            case [command, *values] if command in TABLE_COMMANDS:
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

        if is_data_command:
            _run_data_command(args, metadata, data_dir, select_caches)
        else:
            _run_table_command(args, metadata, filepath, data_dir)
