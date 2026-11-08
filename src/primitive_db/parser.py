QUOTES = ("'", '"')
PUNCTUATION = "(),="


def _quoted_end(expression, start):
    """Найти конец строки с учётом экранированных кавычек."""
    quote = expression[start]
    end = start + 1
    while end < len(expression):
        char = expression[end]
        if char == quote:
            return end + 1
        end += 2 if char == "\\" else 1
    raise ValueError(expression)


def _tokens(expression):
    """Разбить команду на слова, знаки и строки в кавычках."""
    tokens = []
    end = 0
    delimiters = PUNCTUATION + "".join(QUOTES)
    while end < len(expression):
        start = end
        char = expression[start]
        end += 1
        if char.isspace():
            continue
        if char in QUOTES:
            end = _quoted_end(expression, start)
        elif char not in PUNCTUATION:
            while end < len(expression):
                char = expression[end]
                if char.isspace() or char in delimiters:
                    break
                end += 1
        tokens.append(expression[start:end])
    return tokens


def _name(token):
    """Прочитать имя таблицы или столбца."""
    name = _value(token) if token.startswith(QUOTES) else token
    if not name.strip() or token in PUNCTUATION:
        raise ValueError(token)
    return name


def _decode_quoted(token):
    """Снять кавычки и обработать экранирование без потери Unicode."""
    if len(token) < 2 or token[-1] != token[0] or any(c in token for c in "\r\n\0"):
        raise ValueError(token)

    parts = []
    escaped = False
    for char in token[1:-1]:
        if escaped and not char.isascii():
            parts.append("\\")
        parts.append(char)
        escaped = char == "\\" and not escaped

    return "".join(parts).encode("ascii", "backslashreplace").decode("unicode_escape")


def _value(token):
    """Распознать строку, логическое значение или целое число."""
    if token.startswith(QUOTES):
        try:
            return _decode_quoted(token)
        except ValueError as error:
            raise ValueError(token) from error
    if token.lower() in ("true", "false"):
        return token.lower() == "true"
    digits = token[1:] if token.startswith(("+", "-")) else token
    if digits.isascii() and digits.isdecimal():
        return int(token)
    raise ValueError(token)


def _comma_separated(tokens):
    """Разделить список значений или присваиваний по запятым."""
    parts = [[]]
    for token in tokens:
        if token == ",":
            parts.append([])
        else:
            parts[-1].append(token)
    if not all(parts):
        raise ValueError(" ".join(tokens))
    return parts


def _assignment(tokens):
    """Разобрать выражение вида «столбец = значение»."""
    match tokens:
        case [field, "=", value]:
            return _name(field), _value(value)
        case _:
            raise ValueError(" ".join(tokens))


def parse_where(expression):
    """Преобразовать условие WHERE в словарь."""
    field, value = _assignment(_tokens(expression))
    return {field: value}


def parse_set(expression):
    """Преобразовать присваивания SET в словарь новых значений."""
    changes = {}
    for part in _comma_separated(_tokens(expression)):
        field, value = _assignment(part)
        if field in changes:
            raise ValueError(field)
        changes[field] = value
    return changes


def parse_data_command(expression):
    """Вернуть название команды, таблицу и аргументы."""
    match _tokens(expression):
        case ["insert", "into", table, "values", "(", *tokens, ")"]:
            values = []
            for part in _comma_separated(tokens) if tokens else []:
                if len(part) != 1:
                    raise ValueError(" ".join(part))
                values.append(_value(part[0]))
            return "insert", _name(table), values
        case ["select", "from", table]:
            return "select", _name(table), None
        case ["select", "from", table, "where", *condition]:
            return "select", _name(table), parse_where(" ".join(condition))
        case ["update", table, "set", *assignments, "where", field, "=", value]:
            changes = parse_set(" ".join(assignments))
            condition = parse_where(f"{field} = {value}")
            return "update", _name(table), changes, condition
        case ["delete", "from", table, "where", *condition]:
            return "delete", _name(table), parse_where(" ".join(condition))
        case ["info", table]:
            return "info", _name(table)
        case _:
            raise ValueError(expression)
