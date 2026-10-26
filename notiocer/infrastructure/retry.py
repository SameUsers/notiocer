import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

Result = TypeVar('Result')
Parameters = ParamSpec('Parameters')


def retry(
    attempts: int = 4, delay_seconds: float = 1.0
) -> Callable[[Callable[Parameters, Result]], Callable[Parameters, Result]]:
    """Повторяет синхронный вызов при исключении.

    Args:
        attempts: Общее количество попыток, включая первую.
        delay_seconds: Задержка между попытками в секундах.
    """
    if attempts < 1:
        raise ValueError('Количество попыток должно быть положительным')
    if delay_seconds < 0:
        raise ValueError('Задержка не может быть отрицательной')

    def decorator(
        function: Callable[Parameters, Result],
    ) -> Callable[Parameters, Result]:
        """Добавляет повторные попытки к переданной функции."""

        @wraps(function)
        def wrapper(*args: Parameters.args, **kwargs: Parameters.kwargs) -> Result:
            """Вызывает функцию и передаёт последнее исключение после исчерпания попыток."""
            for _ in range(attempts - 1):
                try:
                    return function(*args, **kwargs)
                except Exception:  # noqa: BLE001
                    time.sleep(delay_seconds)
            return function(*args, **kwargs)

        return wrapper

    return decorator
