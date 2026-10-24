from dataclasses import dataclass
from datetime import datetime
from typing import Any, Annotated


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

    client_id: Annotated[Any, "ID клиента"]
    legal_entity: Annotated[str | None, "Юр лицо"]
    subject: Annotated[str | None, "Счет на"]
    invoice_number: Annotated[str | None, "Полный номер счета"]
    invoice_date: Annotated[datetime | None, "Дата счета"]
    invoice_amount: Annotated[float | None, "Сумма счета"]
    balance: Annotated[float | None, "Сальдо"]
    currency: Annotated[str | None, "Валюта"]
    category: Annotated[str | None, "Категория"]
    payment_due_date: Annotated[datetime | None, "Срок оплаты"]
    sign: Annotated[str | None, "Предоплата до загрузки"]
    employee: Annotated[str | None, "Сотрудник"]
    equipment_service: Annotated[str | None, "Услуга отдела оборудования"]
    transport_reference: Annotated[str | None, "Номер контейнера / AWB /авто"]
    unloading_date: Annotated[datetime | None, "Дата выгрузки"]
    sfb_curator: Annotated[str | None, "Куратор СФБ"]
    shipping_date: Annotated[datetime | None, "Дата отгрузки"]
    estimated_arrival_date: Annotated[datetime | None, "Прогнозная ETA"]
    market: Annotated[str | None, "Рынок"]
    payment_service: Annotated[str | None, "Сервис для срока оплаты"]
    payment_terms_type: Annotated[str | None, "Тип платежных условий"]
    contract_details: Annotated[str | None, "№ и дата договора"]
    service_type: Annotated[str | None, "Тип сервиса"]
    partial_prepayment: Annotated[Any, "Частичная предоплата"]
    partial_prepayment_terms: Annotated[str | None, "Условия частичной предоплаты"]
    payment_terms: Annotated[str | None, "Крайний момент оплаты"]
    calculated_payment_term: Annotated[Any, "Расчетный с/о"]
