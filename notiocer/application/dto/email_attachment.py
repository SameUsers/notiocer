from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAttachment:
    """Имя, MIME-тип и содержимое почтового вложения."""

    filename: str
    content_type: str
    content: bytes
