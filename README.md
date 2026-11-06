# Примитивная база данных

Консольная программа для создания, просмотра и удаления таблиц. Имена таблиц и
структура столбцов сохраняются в `db_meta.json` в папке, из которой запущена
программа.

## Установка и запуск

```bash
uv build
uv tool install dist/primitive_db-0.3.0-py3-none-any.whl
database
```

В папке проекта также можно запустить `uv run database`.

## Управление таблицами

| Команда | Действие |
| --- | --- |
| `create_table <имя> <столбец:тип> ...` | Создать таблицу. Поддерживаются `int`, `str` и `bool`. Столбец `ID:int` идёт первым. |
| `list_tables` | Показать список таблиц. |
| `drop_table <имя>` | Удалить таблицу. |
| `help` | Показать справку. |
| `exit` | Выйти из программы. |

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
Введите команду: list_tables
- users
Введите команду: drop_table users
Таблица "users" успешно удалена.
Введите команду: exit
```

## Демонстрация в терминале

[![Установка пакета и управление таблицей](https://asciinema.org/a/Qy45TPXwILesOGQ6.svg)](https://asciinema.org/a/Qy45TPXwILesOGQ6)

[Скачать запись `.cast`](docs/database-demo.cast) для локального просмотра.
