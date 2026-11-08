import re
from ast import literal_eval

DATA_COMMANDS = {"insert", "select", "update", "delete", "info"}
TOKEN = re.compile(
    r""""(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[(),=]|[^\s(),="']+"""
)


def _tokens(expression):
    tokens = []
    end = 0
    for match in TOKEN.finditer(expression):
        if expression[end:match.start()].strip():
            raise ValueError(expression)
        tokens.append(match.group())
        end = match.end()
    if expression[end:].strip():
        raise ValueError(expression)
    return tokens


def _name(token):
    name = _value(token) if token.startswith(("'", '"')) else token
    if not name.strip() or token in {"(", ")", ",", "="}:
        raise ValueError(token)
    return name


def _value(token):
    if token.startswith(("'", '"')):
        try:
            return literal_eval(token)
        except (SyntaxError, ValueError) as error:
            raise ValueError(token) from error
    if token.lower() in ("true", "false"):
        return token.lower() == "true"
    if re.fullmatch(r"[+-]?[0-9]+", token):
        return int(token)
    raise ValueError(token)


def _comma_separated(tokens):
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
    match tokens:
        case [field, "=", value]:
            return _name(field), _value(value)
        case _:
            raise ValueError(" ".join(tokens))


def parse_where(expression):
    field, value = _assignment(_tokens(expression))
    return {field: value}


def parse_set(expression):
    changes = {}
    for part in _comma_separated(_tokens(expression)):
        field, value = _assignment(part)
        if field in changes:
            raise ValueError(field)
        changes[field] = value
    return changes


def parse_data_command(expression):
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
