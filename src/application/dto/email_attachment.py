from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAttachment:
    """Неизменяемое представление файла, прикреплённого к письму.

    Атрибуты:
        filename: Имя прикреплённого файла.
        content_type: MIME-тип содержимого вложения.
        content: Сырые байты вложения.
    """

    filename: str
    content_type: str
    content: bytes
