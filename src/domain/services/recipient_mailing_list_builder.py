from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from ..entity.invoice import Invoice


class RecipientMailingListBuilder:
    """Группирует отобранные счета по адресу электронной почты получателя.

    Маршрутизация получателей зависит от платёжного сервиса и рынка
    счёта: одни сервисы направляются в фиксированные общие почтовые ящики,
    а другие — ответственному сотруднику.
    """

    def build(
        self, selected_invoices: Iterable[Invoice]
    ) -> dict[str | None, list[Invoice]]:
        """Группирует счета по получателю.

        Проходит по переданным счетам и назначает каждый из них
        получателю на основе его платёжного сервиса и рынка. Сервисы с
        выделенным общим почтовым ящиком направляются туда; остальные сервисы
        направляются ответственному сотруднику. Счёт может быть добавлен
        более чем одному получателю, если он соответствует нескольким правилам.

        Args:
            selected_invoices: Счета, которые нужно сгруппировать по получателю.

        Returns:
            Отображение получателя (адрес электронной почты или идентификатор
            сотрудника) на счета, адресованные ему.
        """
        cmtd_services = {'Море', 'ЖД', 'Море+ЖД', 'Авто.ДКП', 'Иное.ДКП'}
        invoices_by_recipient: dict[str, list[Any]] = defaultdict(list)
        for invoice in selected_invoices:
            if invoice.payment_service in cmtd_services:
                if invoice.market == 'РБ':
                    invoices_by_recipient['CMTD_BY_CM@stalogistic.com'].append(invoice)
                elif invoice.market == 'РФ':
                    invoices_by_recipient['CMTD_RU_CM@stalogistic.com'].append(invoice)
                else:
                    invoices_by_recipient['ctd_cm@stalogistic.com'].append(invoice)

            if invoice.payment_service in {'Авиа'} and invoice.market == 'РБ':
                invoices_by_recipient['CM_Air_BY@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'Авиа'} and invoice.market == 'РФ':
                invoices_by_recipient['cm-air-ru@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'Авиа'} and invoice.market not in {
                'РФ',
                'РБ',
            }:
                invoices_by_recipient['air@stalogistic.com'].append(invoice)

            if invoice.payment_service in {'ОКГ'} and invoice.market == 'РБ':
                invoices_by_recipient['ftl_cm_by@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОКГ'} and invoice.market == 'РФ':
                invoices_by_recipient['FTL_CM_RU@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОКГ'} and invoice.market == 'Узбекистан':
                invoices_by_recipient['FTL_CM_UZ@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОКГ'} and invoice.market == 'Казахстан':
                invoices_by_recipient['FTL_CM_KZ@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОКГ'} and invoice.market not in {
                'РБ',
                'РФ',
                'Узбекистан',
                'Казахстан',
            }:
                invoices_by_recipient[invoice.employee].append(invoice)

            if invoice.payment_service in {'ОВС'}:
                invoices_by_recipient['ovs@stalogistic.com'].append(invoice)

            if invoice.payment_service in {'ОСГ'} and invoice.market == 'РБ':
                invoices_by_recipient['KM_SG_RB@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОСГ'} and invoice.market == 'РФ':
                invoices_by_recipient['KM_SG_RF@stalogistic.com'].append(invoice)
            elif invoice.payment_service in {'ОСГ'} and invoice.market not in {
                'РБ',
                'РФ',
            }:
                invoices_by_recipient['km_sg@stalogistic.com'].append(invoice)

            if invoice.payment_service == 'Проекты':
                invoices_by_recipient['oog@stalogistic.com'].append(invoice)

            if invoice.payment_service in {'ТО', 'TC', 'ТО и ТС'}:
                invoices_by_recipient['csd2@stalogistic.com'].append(invoice)

            if invoice.payment_service in {'Тшк'}:
                invoices_by_recipient[invoice.employee].append(invoice)

            if invoice.payment_service in {'Алм'}:
                invoices_by_recipient[invoice.employee].append(invoice)

            if invoice.payment_service in {'ЛГВ'}:
                invoices_by_recipient[invoice.employee].append(invoice)

            if invoice.payment_service in {'Склад'}:
                invoices_by_recipient[invoice.employee].append(invoice)

            if invoice.payment_service:
                invoices_by_recipient[invoice.employee].append(invoice)
        return invoices_by_recipient
