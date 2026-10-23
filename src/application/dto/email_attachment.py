from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content_type: str
    content: bytes
