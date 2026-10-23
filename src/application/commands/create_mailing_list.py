from dataclasses import dataclass


@dataclass
class CreateMailingListCommand:
    excel_bytes: bytes
