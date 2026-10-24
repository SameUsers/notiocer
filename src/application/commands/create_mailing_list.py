from dataclasses import dataclass


@dataclass
class CreateMailingListCommand:
    """Входная команда для создания списка рассылки из книги Excel.

    Атрибуты:
        excel_bytes: Сырое содержимое файла ``.xlsx`` для обработки.
    """

    excel_bytes: bytes
