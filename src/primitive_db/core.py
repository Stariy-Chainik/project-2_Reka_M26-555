from primitive_db.utils import load_table_data

COLUMN_TYPES = {"int": int, "str": str, "bool": bool}
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


def table_schema(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return dict(column.split(":", 1) for column in metadata[table_name])


def validate_values(schema, values):
    for column, value in values.items():
        if column not in schema:
            raise ValueError(f'Столбец "{column}" не существует.')
        column_type = schema[column]
        if type(value) is not COLUMN_TYPES[column_type]:
            raise ValueError(
                f'Для столбца "{column}" ожидается значение типа {column_type}.'
            )


def insert(metadata, table_name, values, *, table_data=None):
    schema = table_schema(metadata, table_name)
    columns = [column for column in schema if column != "ID"]
    if len(values) != len(columns):
        raise ValueError(
            f"Ожидается значений: {len(columns)}, получено: {len(values)}."
        )

    record = dict(zip(columns, values, strict=True))
    validate_values(schema, record)
    if table_data is None:
        table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    return [*table_data, {"ID": new_id, **record}]


def _matches(row, where_clause):
    return all(
        column in row and type(row[column]) is type(value) and row[column] == value
        for column, value in where_clause.items()
    )


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data
    return [row for row in table_data if _matches(row, where_clause)]


def update(table_data, set_clause, where_clause):
    if "ID" in set_clause:
        raise ValueError("Столбец ID нельзя менять.")
    if not where_clause:
        raise ValueError("Укажите условие where.")
    return [
        row | set_clause if _matches(row, where_clause) else row
        for row in table_data
    ]


def delete(table_data, where_clause):
    if not where_clause:
        raise ValueError("Укажите условие where.")
    return [row for row in table_data if not _matches(row, where_clause)]
