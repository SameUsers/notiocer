from typing import Protocol

from src.application.commands.create_mailing_list import CreateMailingListCommand


class CreateMailingListFromExcelUseCase(Protocol):
    def execute(self, command: CreateMailingListCommand) -> None: ...
