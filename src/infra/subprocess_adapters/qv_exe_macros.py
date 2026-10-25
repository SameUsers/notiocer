import subprocess
from collections.abc import Sequence


class QlikViewMacrosRunner:
    """Запускает макрос QlikView через :mod:`subprocess`.

    Вызывает внешний исполняемый файл QlikView с аргументами,
    заданными при создании, и дожидается завершения с таймаутом.
    """

    def __init__(
        self,
        command: Sequence[str],
        timeout: float,
    ) -> None:
        """Инициализирует раннер.

        Args:
            command: Аргументы команды (первый — путь к исполняемому файлу QlikView).
            timeout: Максимальное время ожидания завершения в секундах.
        """
        self._command = list(command)
        self._timeout = timeout

    def run(self) -> None:
        """Запускает макрос и дожидается завершения.

        Raises:
            RuntimeError: Если QlikView завершился с ненулевым кодом возврата.
            TimeoutError: Если выполнение превысило заданный таймаут.
        """
        try:
            subprocess.run(
                self._command,
                timeout=self._timeout,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired as error:
            raise TimeoutError(
                f'QlikView не завершился за {self._timeout} секунд'
            ) from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f'QlikView завершился с кодом {error.returncode}: {error.stderr}'
            ) from error
