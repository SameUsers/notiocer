from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Invoice:
    """Неизменяемое представление одной строки счёта.

    Отражает поля записи счёта в том виде, в каком они читаются из
    исходной книги. Большинство полей необязательны, поскольку исходные данные
    могут быть неполными.

    Атрибуты:
        client_id: Идентификатор клиента, которому принадлежит счёт.
        legal_entity: Юридическое лицо, связанное со счётом.
        subject: Тема или краткое описание счёта.
        invoice_number: Номер счёта.
        invoice_date: Дата выставления счёта.
        invoice_amount: Общая сумма счёта.
        balance: Непогашенный остаток по счёту.
        currency: Валюта сумм.
        category: Категория счёта.
        payment_due_date: Дата, к которой должен быть произведён платёж.
        sign: Признак-маркер, связанный со счётом.
        employee: Сотрудник, ответственный за счёт.
        equipment_service: Ссылка на сервисное обслуживание оборудования.
        transport_reference: Транспортная ссылка.
        unloading_date: Дата разгрузки.
        sfb_curator: Куратор SFB, назначенный на счёт.
        shipping_date: Дата отгрузки.
        estimated_arrival_date: Ожидаемая дата прибытия.
        market: Рынок, к которому относится счёт.
        payment_service: Платёжный сервис, связанный со счётом.
        payment_terms_type: Тип условий оплаты.
        contract_details: Детали договора.
        service_type: Тип предоставляемой услуги.
        partial_prepayment: Информация о частичной предоплате.
        partial_prepayment_terms: Условия частичной предоплаты.
        payment_terms: Условия оплаты.
        calculated_payment_term: Расчётный срок оплаты.
    """

    client_id: Any
    legal_entity: str | None
    subject: str | None
    invoice_number: str | None
    invoice_date: datetime | None
    invoice_amount: float | None
    balance: float | None
    currency: str | None
    category: str | None
    payment_due_date: datetime | None
    sign: str | None
    employee: str | None
    equipment_service: str | None
    transport_reference: str | None
    unloading_date: datetime | None
    sfb_curator: str | None
    shipping_date: datetime | None
    estimated_arrival_date: datetime | None
    market: str | None
    payment_service: str | None
    payment_terms_type: str | None
    contract_details: str | None
    service_type: str | None
    partial_prepayment: Any
    partial_prepayment_terms: str | None
    payment_terms: str | None
    calculated_payment_term: Any
