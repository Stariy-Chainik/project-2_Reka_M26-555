COLUMN_TYPES = {"int", "str", "bool"}
INVALID_VALUE = "Некорректное значение: {}. Попробуйте снова."


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    if not table_name.strip() or not columns:
        print(INVALID_VALUE.format(table_name))
        return metadata

    table_columns = ["ID:int"]
    column_names = set()
    for column in columns:
        name, _, column_type = column.partition(":")
        name = name.strip()
        if name.casefold() == "id":
            name = "ID"
        if (
            not name
            or column_type not in COLUMN_TYPES
            or name in column_names
            or (name == "ID" and column_type != "int")
        ):
            print(INVALID_VALUE.format(column))
            return metadata

        column_names.add(name)
        if name != "ID":
            table_columns.append(f"{name}:{column_type}")

    metadata[table_name] = table_columns
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    return metadata
