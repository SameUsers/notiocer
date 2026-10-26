import os
import subprocess
from collections.abc import Sequence


class QlikViewProcessRunner:
    """Запускает QlikView с переданными аргументами и ограничением времени."""

    def __init__(
        self,
        command: Sequence[str],
        timeout_seconds: float,
    ) -> None:
        """Принимает аргументы команды и таймаут в секундах."""
        self._command = list(command)
        self._timeout_seconds = timeout_seconds

    def run(self) -> None:
        """Запускает команду и ждёт завершения.

        Raises:
            RuntimeError: Процесс завершился с ненулевым кодом.
            TimeoutError: Процесс не завершился за отведённое время.
        """
        try:
            subprocess.run(
                self._command,
                timeout=self._timeout_seconds,
                check=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
        except subprocess.TimeoutExpired as error:
            raise TimeoutError(
                f'QlikView не завершился за {self._timeout_seconds} секунд'
            ) from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f'QlikView завершился с кодом {error.returncode}: {error.stderr}'
            ) from error
