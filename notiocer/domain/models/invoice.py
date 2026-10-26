from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any


@dataclass(frozen=True)
class Invoice:
    """Данные одного счёта из отчёта; отсутствующие значения допускаются."""

    client_id: Annotated[Any, 'ID клиента']
    legal_entity: Annotated[str | None, 'Юр лицо']
    billing_subject: Annotated[str | None, 'Счет на']
    invoice_number: Annotated[str | None, 'Полный номер счета']
    invoice_date: Annotated[datetime | None, 'Дата счета']
    invoice_amount: Annotated[float | None, 'Сумма счета']
    balance: Annotated[float | None, 'Сальдо']
    currency: Annotated[str | None, 'Валюта']
    category: Annotated[str | None, 'Категория']
    payment_due_date: Annotated[datetime | None, 'Срок оплаты']
    prepayment_before_loading: Annotated[str | None, 'Предоплата до загрузки']
    employee_id: Annotated[str | None, 'Сотрудник']
    equipment_service: Annotated[str | None, 'Услуга отдела оборудования']
    transport_reference: Annotated[str | None, 'Номер контейнера / AWB /авто']
    unloading_date: Annotated[datetime | None, 'Дата выгрузки']
    sfb_curator: Annotated[str | None, 'Куратор СФБ']
    shipping_date: Annotated[datetime | None, 'Дата отгрузки']
    estimated_arrival_date: Annotated[datetime | None, 'Прогнозная ETA']
    market: Annotated[str | None, 'Рынок']
    payment_service: Annotated[str | None, 'Сервис для срока оплаты']
    payment_terms_type: Annotated[str | None, 'Тип платежных условий']
    contract_details: Annotated[str | None, '№ и дата договора']
    service_type: Annotated[str | None, 'Тип сервиса']
    partial_prepayment: Annotated[Any, 'Частичная предоплата']
    partial_prepayment_terms: Annotated[str | None, 'Условия частичной предоплаты']
    payment_milestone: Annotated[str | None, 'Крайний момент оплаты']
    calculated_payment_term: Annotated[Any, 'Расчетный с/о']
