from typing import Protocol


class EmployeeEmailLookup(Protocol):
    """Протокол для определения email сотрудника по его идентификатору."""

    def get_email(self, employee_id: str) -> str | None:
        """Возвращает адрес электронной почты, связанный с указанным сотрудником.

        Args:
            employee_id: Идентификатор сотрудника для поиска.

        Returns:
            Адрес электронной почты сотрудника или ``None``, если email не найден.
        """
        ...
