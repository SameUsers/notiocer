from typing import Protocol


class EmployeeEmailLookup(Protocol):
    """Порт поиска почтового адреса по идентификатору сотрудника."""

    def get_email(self, employee_id: str) -> str | None:
        """Возвращает email сотрудника или None, если адрес не найден."""
        ...
