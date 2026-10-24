"""Доменный слой проекта notiocer.

Содержит бизнес-сущности и сервисы, выражающие правила предметной
области рассылки счетов. Слой не зависит от инфраструктуры и
прикладного слоя: здесь нет ни чтения файлов, ни отправки почты,
ни знания о том, откуда пришли данные.

Состав пакета:

- :class:`Invoice` — неизменяемая сущность одной строки счёта,
  отражающая поля записи из исходной книги Excel;
- :class:`InvoiceMessage` — неизменяемое сообщение, группирующее
  счета для одного получателя;
- :class:`InvoiceMessageBuilder` — доменный сервис, формирующий
  сообщения со счетами для каждого получателя, разрешая email
  сотрудников через порт ``EmployeeEmailLookup``;
- :class:`MailingInvoiceSelector` — доменный сервис, отбирающий
  счета, подходящие для рассылки, по категории, возрасту счёта
  и условиям оплаты;
- :class:`RecipientMailingListBuilder` — доменный сервис,
  группирующий отобранные счета по получателям на основе
  платёжного сервиса и рынка счёта.

Ключевые принципы:

- сущности (:class:`Invoice`, :class:`InvoiceMessage`) неизменяемы
  (``frozen=True``), чтобы их можно было безопасно передавать между
  слоями и использовать в множествах/словарях;
- правила отбора и маршрутизации счетов живут именно здесь, а не
  в адаптерах ``infra`` — это позволяет менять источники данных
  и способы отправки, не трогая бизнес-логику;
- сервисы домена зависят только от сущностей и портов
  (через ``typing.Protocol``), но не от конкретных реализаций.
"""

from .entity.invoice import Invoice
from .entity.invoice_message import InvoiceMessage
from .services.invoice_message_builder import InvoiceMessageBuilder
from .services.mailing_invoice_selector import MailingInvoiceSelector
from .services.recipient_mailing_list_builder import RecipientMailingListBuilder

__all__ = [
    'Invoice',
    'InvoiceMessage',
    'InvoiceMessageBuilder',
    'MailingInvoiceSelector',
    'RecipientMailingListBuilder',
]
