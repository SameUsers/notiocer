"""Прикладной слой проекта notiocer.

Содержит сценарии использования (use cases), входные команды,
DTO для передачи данных между слоями и порты — абстракции внешних
зависимостей, которые реализуются в слое ``infra``. Слой знает про
домен, но не знает про конкретные технологии: файлы, почту и внешние
системы он видит только через порты.

Состав пакета:

Команды и DTO:

- :class:`CreateMailingListCommand` — входная команда с сырыми
  байтами книги Excel для обработки;
- :class:`EmailAttachment` — неизменяемое представление файла,
  прикреплённого к письму;
- :class:`PreparedInvoiceMessage` — неизменяемое email-сообщение,
  готовое к отправке: получатель, счета и вложение.

Сценарии использования:

- :class:`CreateMailingListFromExcelInteractor` — реализация сценария
  «создать и разослать список счетов из Excel»: чтение книги,
  отбор счетов, группировка по получателям, сборка сообщений
  с вложениями и отправка;
- :class:`CreateMailingListFromExcelUseCase` — протокол этого
  сценария, от которого зависят контроллеры.

Порты (абстракции внешних зависимостей):

- :class:`EmailSender` — отправка подготовленных сообщений по email;
- :class:`EmployeeEmailLookup` — определение email сотрудника
  по его идентификатору;
- :class:`InvoiceAttachmentBuilder` — формирование email-вложения
  из набора счетов;
- :class:`InvoiceExcelReader` — чтение счетов из книги Excel
  (жизненный цикл ``load`` → ``read_invoices`` → ``unload``).

Ключевые принципы:

- зависимости направлены внутрь: ``application`` зависит от ``domain``,
  а ``infra`` зависит от портов ``application``, но не наоборот;
- взаимодействие с внешним миром — только через ``Protocol``-порты,
  что позволяет подменять реализации в тестах и менять технологии
  без правок сценариев;
- DTO и команды неизменяемы (``frozen=True``), чтобы их можно было
  безопасно передавать между слоями.
"""

from .commands.create_mailing_list import CreateMailingListCommand
from .dto.email_attachment import EmailAttachment
from .dto.prepared_invoice_message import PreparedInvoiceMessage
from .interactors.create_mailing_list_from_excel import (
    CreateMailingListFromExcelInteractor,
)
from .ports.create_mailing_list_from_excel import CreateMailingListFromExcelUseCase
from .ports.email_sender import EmailSender
from .ports.employee_email_lookup import EmployeeEmailLookup
from .ports.invoice_attachment_builder import InvoiceAttachmentBuilder
from .ports.invoice_excel_reader import InvoiceExcelReader

__all__ = [
    'CreateMailingListCommand',
    'EmailAttachment',
    'PreparedInvoiceMessage',
    'CreateMailingListFromExcelInteractor',
    'CreateMailingListFromExcelUseCase',
    'EmailSender',
    'EmployeeEmailLookup',
    'InvoiceAttachmentBuilder',
    'InvoiceExcelReader',
]
