from pathlib import Path

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.ports.create_mailing_list_from_excel import (
    CreateMailingListFromExcelUseCase,
)


class LocalExcelReportController:
    """Контроллер, запускающий поток создания списка рассылки по локальному файлу Excel.

    Читает книгу с диска, оборачивает её в команду и делегирует
    выполнение сценарию использования списка рассылки.
    """

    def __init__(
        self, report_path: Path, use_case: CreateMailingListFromExcelUseCase
    ) -> None:
        """Инициализирует контроллер.

        Args:
            report_path: Путь к обрабатываемому отчёту Excel.
            use_case: Сценарий использования, который создаёт список рассылки из отчёта.
        """
        self._report_path = report_path
        self._use_case = use_case

    def _read_excel_report(self) -> bytes:
        """Читает отчёт Excel с диска.

        Returns:
            Сырые байты файла отчёта.
        """
        return self._report_path.read_bytes()

    def run(self) -> None:
        """Читает отчёт Excel и выполняет сценарий использования списка рассылки."""
        excel_bytes = self._read_excel_report()
        command = CreateMailingListCommand(excel_bytes=excel_bytes)
        self._use_case.execute(command=command)
