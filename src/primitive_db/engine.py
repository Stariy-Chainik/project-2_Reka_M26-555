import shlex
from pathlib import Path

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    INVALID_VALUE,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    table_schema,
    update,
    validate_values,
)
from primitive_db.parser import DATA_COMMANDS, parse_data_command
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
    print(HELP)


def _run_table_command(args, metadata, filepath, data_dir):
    table_count = len(metadata)
    match args:
        case ["list_tables"]:
            if not metadata:
                print("Таблиц пока нет.")
            for table_name in metadata:
                print(f"- {table_name}")
        case ["create_table", table_name, *columns]:
            metadata = create_table(metadata, table_name, columns)
            if len(metadata) != table_count:
                save_table_data(table_name, [], data_dir)
                save_metadata(filepath, metadata)
                column_list = ", ".join(metadata[table_name])
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: '
                    f"{column_list}"
                )
        case ["drop_table", table_name]:
            metadata = drop_table(metadata, table_name)
            if len(metadata) != table_count:
                save_metadata(filepath, metadata)
                remove_table_data(table_name, data_dir)
                print(f'Таблица "{table_name}" успешно удалена.')


def _run_data_command(args, metadata, data_dir):
    _, table_name, *_ = args
    schema = table_schema(metadata, table_name)
    rows = load_table_data(table_name, data_dir)
    for row in rows:
        if row.keys() != schema.keys():
            raise ValueError(f'Запись в таблице "{table_name}" не соответствует схеме.')
        validate_values(schema, row)

    match args:
        case ["info", _]:
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {', '.join(metadata[table_name])}")
            print(f"Количество записей: {len(rows)}")
            return
        case ["select", _, condition]:
            if condition is not None:
                validate_values(schema, condition)
            table = PrettyTable(list(schema))
            selected = select(rows, condition)
            table.add_rows([[row[column] for column in schema] for row in selected])
            print(table)
            return
        case ["insert", _, values]:
            updated = insert(metadata, table_name, values, table_data=rows)
            affected = updated[-1:]
            message = 'успешно добавлена в таблицу "{table_name}".'
        case ["update", _, changes, condition]:
            validate_values(schema, changes)
            validate_values(schema, condition)
            affected = select(rows, condition)
            updated = update(rows, changes, condition)
            message = 'в таблице "{table_name}" успешно обновлена.'
        case ["delete", _, condition]:
            validate_values(schema, condition)
            affected = select(rows, condition)
            updated = delete(rows, condition)
            message = 'успешно удалена из таблицы "{table_name}".'

    if not affected:
        print("Подходящих записей нет.")
        return
    save_table_data(table_name, updated, data_dir)
    for row in affected:
        print(f'Запись с ID={row["ID"]} {message.format(table_name=table_name)}')


def run(filepath="db_meta.json") -> None:
    data_dir = Path(filepath).parent / "data"
    print_help()

    while True:
        try:
            user_input = prompt.string("Введите команду: ")
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

        try:
            if is_data_command:
                _run_data_command(args, metadata, data_dir)
            else:
                _run_table_command(args, metadata, filepath, data_dir)
        except (OSError, ValueError) as error:
            print(f"Ошибка: {error}")
