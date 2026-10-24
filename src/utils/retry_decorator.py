import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T')


def retry_sync(
    count: int = 4, delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Декоратор, повторяющий вызов синхронной функции при исключении.

    Args:
        count: Максимальное количество попыток.
        delay: Задержка между попытками в секундах.

    Returns:
        Декоратор, оборачивающий функцию логикой повторных попыток.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapped(*args: Any, **kwargs: Any) -> T:
            last_error: Exception | None = None
            for attempt in range(1, count + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as error:  # noqa: BLE001
                    last_error = error
                    if attempt < count:
                        time.sleep(delay)
            assert last_error is not None
            raise last_error

        return wrapped

    return decorator
