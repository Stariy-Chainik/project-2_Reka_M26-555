# Примитивная база данных

Консольная база данных для работы с таблицами и записями. Схемы сохраняются в
`db_meta.json`, а записи каждой таблицы хранятся в отдельном файле в папке `data/`.
Оба пути отсчитываются от папки, из которой запущена программа.

## Установка и запуск

```bash
uv build
uv tool install dist/primitive_db-0.4.0-py3-none-any.whl
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

## CRUD-операции

Сначала создайте таблицу, например `create_table users name:str age:int is_active:bool`.
Передавайте значения в порядке столбцов. Все поля обязательны, а `ID` создаётся
автоматически. Строки заключайте в кавычки, целые числа и `true`/`false` вводите
без кавычек.

| Команда | Действие |
| --- | --- |
| `insert into users values ("Sergei", 28, true)` | Добавить запись. |
| `select from users` | Показать все записи. |
| `select from users where age = 28` | Показать записи по условию. |
| `update users set age = 29 where name = "Sergei"` | Обновить все подходящие записи. |
| `delete from users where ID = 1` | Удалить все подходящие записи. |
| `info users` | Показать столбцы, их типы и число записей. |

В `set` можно перечислить несколько присваиваний через запятую. `ID` доступен в
условии `where`, менять его через `set` нельзя. Команда `drop_table` удаляет
схему таблицы и файл с её записями.

[![Демонстрация CRUD-операций](https://asciinema.org/a/y2AlmmkavwyFZ7lR.svg)](https://asciinema.org/a/y2AlmmkavwyFZ7lR)

[Скачать запись CRUD-операций `.cast`](docs/database-crud-demo.cast) для локального просмотра.
