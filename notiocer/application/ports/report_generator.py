from typing import Protocol


class ReportGenerator(Protocol):
    """Порт генерации исходного отчёта для рассылки."""

    def generate(self) -> None:
        """Генерирует отчёт и ожидает завершения операции."""
        ...
