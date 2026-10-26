from collections import defaultdict
from collections.abc import Iterable

from notiocer.domain.models.invoice import Invoice
from notiocer.domain.models.invoice_routing_rules import InvoiceRoutingRules


class InvoiceRecipientRouter:
    """Группирует счета по всем подходящим правилам без повторов у одного получателя."""

    def __init__(self, routing_rules: InvoiceRoutingRules) -> None:
        """Принимает проверенные правила маршрутизации."""
        self._routing_rules = routing_rules.rules

    def route(
        self,
        invoices: Iterable[Invoice],
    ) -> dict[str | None, list[Invoice]]:
        """Выбирает получателей по сервису и рынку, используя default для неизвестного рынка."""
        invoices_by_recipient: dict[str | None, list[Invoice]] = defaultdict(list)

        for invoice in invoices:
            routed_recipients: set[str] = set()
            for rule in self._routing_rules:
                if invoice.payment_service not in rule.services:
                    continue

                recipient_reference: str | None = rule.recipients['default']
                if invoice.market is not None:
                    recipient_reference = rule.recipients.get(
                        invoice.market,
                        rule.recipients['default'],
                    )

                if recipient_reference == 'employee':
                    recipient_reference = invoice.employee_id

                if not recipient_reference or recipient_reference in routed_recipients:
                    continue
                invoices_by_recipient[recipient_reference].append(invoice)
                routed_recipients.add(recipient_reference)

        return dict(invoices_by_recipient)
