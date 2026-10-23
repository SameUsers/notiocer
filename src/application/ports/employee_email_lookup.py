from typing import Protocol


class EmployeeEmailLookup(Protocol):
    def get_email(self, employee_name: str) -> str:
        ...
