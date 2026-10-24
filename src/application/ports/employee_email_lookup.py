from typing import Protocol


class EmployeeEmailLookup(Protocol):
    def get_email(self, employee_id: str) -> str | None: ...
