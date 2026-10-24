"""Инфраструктурный слой проекта notiocer.

Реализует адаптеры к внешним системам и конкретные технологии,
которые подключаются к портам прикладного слоя (application/ports).
Здесь находятся:

- :class:`AxEmployeeEmailLookup` — поиск email сотрудников в системе AX
  (адаптер к ``EmployeeEmailLookup``);
- :class:`OpenpyxlInvoiceReader` — чтение счетов из ``.xlsx`` через openpyxl
  (адаптер к ``InvoiceExcelReader``);
- :class:`XlrdInvoiceReader` — чтение счетов из ``.xls`` через xlrd
  (адаптер к ``InvoiceExcelReader``);
- :class:`OpenpyxlInvoiceAttachmentBuilder` — сборка вложений-отчётов Excel
  через openpyxl (адаптер к ``InvoiceAttachmentBuilder``);
- :class:`ExchangeEmailSender` — отправка писем через Exchange
  (адаптер к ``EmailSender``).

Пакет не содержит бизнес-логики: все решения о том, какие счета
отбирать, как группировать и какие тексты формировать, принимаются
в слоях ``domain`` и ``application``. Задача ``infra`` — только
взаимодействие с файлами, почтой и внешними сервисами.
"""

from .ax_adapters.employee_email_lookup import AxEmployeeEmailLookup
from .excel_readers.openpyxl_invoice_reader import OpenpyxlInvoiceReader
from .excel_readers.xlrd_invoice_reader import XlrdInvoiceReader
from .excel_writers.openpyxl_invoice_attachment_builder import (
    OpenpyxlInvoiceAttachmentBuilder,
)
from .exchange_adapters.exchange_email_sender import ExchangeEmailSender

__all__ = [
    'AxEmployeeEmailLookup',
    'OpenpyxlInvoiceReader',
    'XlrdInvoiceReader',
    'OpenpyxlInvoiceAttachmentBuilder',
    'ExchangeEmailSender',
]
