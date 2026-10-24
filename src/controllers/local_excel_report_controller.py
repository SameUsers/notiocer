from pathlib import Path

from src.application.commands.create_mailing_list import CreateMailingListCommand
from src.application.ports.create_mailing_list_from_excel import (
    CreateMailingListFromExcelUseCase,
)


class LocalExcelReportController:
    def __init__(
        self, report_path: Path, use_case: CreateMailingListFromExcelUseCase
    ) -> None:
        self._report_path = report_path
        self._use_case = use_case

    def _read_excel_report(self) -> bytes:
        return self._report_path.read_bytes()

    def run(self) -> None:
        excel_bytes = self._read_excel_report()
        command = CreateMailingListCommand(excel_bytes=excel_bytes)
        self._use_case.execute(command=command)
