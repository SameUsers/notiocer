from typing import Protocol

from src.application.commands.create_mailing_list import CreateMailingListCommand


class CreateMailingListFromExcelUseCase(Protocol):
    """Протокол для создания списка рассылки из источника Excel."""

    def execute(self, command: CreateMailingListCommand) -> None:
        """Выполняет поток создания списка рассылки.

        Args:
            command: Входные данные, описывающие создаваемый список рассылки.
        """
        ...
