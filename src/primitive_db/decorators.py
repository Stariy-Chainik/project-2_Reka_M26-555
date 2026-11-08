import time

from primitive_db.constants import CONFIRM_ANSWER


def _preserve_function_info(func, wrapper):
    """Передать обёртке имя, описание и ссылку на исходную функцию."""
    attributes = (
        "__module__", "__name__", "__qualname__", "__doc__", "__annotations__"
    )
    for attribute in attributes:
        if hasattr(func, attribute):
            setattr(wrapper, attribute, getattr(func, attribute))
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func):
    """Преобразовать ошибки базы в сообщения для пользователя."""

    def wrapper(*args, **kwargs):
        """Выполнить операцию и обработать ошибки ключей, значений и файлов."""
        try:
            return func(*args, **kwargs)
        except KeyError as error:
            message = error.args[0] if error.args else "Ключ не найден."
            print(f"Ошибка: {message}")
        except (ValueError, OSError) as error:
            # OSError включает FileNotFoundError.
            print(f"Ошибка: {error}")
        return None

    return _preserve_function_info(func, wrapper)


def confirm_action(action_name):
    """Создать декоратор, запрашивающий подтверждение действия."""

    def decorator(func):
        """Защитить операцию запросом подтверждения."""

        def wrapper(*args, **kwargs):
            """Выполнить операцию только после подтверждения."""
            try:
                answer = input(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            except (EOFError, KeyboardInterrupt):
                answer = ""

            if answer != CONFIRM_ANSWER:
                print("Действие отменено.")
                return None
            return func(*args, **kwargs)

        return _preserve_function_info(func, wrapper)

    return decorator


def log_time(func):
    """Вывести длительность работы функции."""

    def wrapper(*args, **kwargs):
        """Замерить время и вернуть исходный результат."""
        started = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return _preserve_function_info(func, wrapper)


def create_cacher():
    """Создать независимый кэш результатов."""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть результат по ключу или вычислить его при первом запросе."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
