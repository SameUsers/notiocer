from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class InvoiceRoutingRule(BaseModel):
    """Маршрут для сервисов по рынкам с обязательным default; employee обозначает сотрудника счёта."""

    model_config = ConfigDict(extra='forbid')

    services: set[NonEmptyString] = Field(min_length=1)
    recipients: dict[NonEmptyString, NonEmptyString]

    @model_validator(mode='after')
    def validate_recipients(self) -> 'InvoiceRoutingRule':
        """Проверяет наличие default и формат получателей: email или employee."""
        if 'default' not in self.recipients:
            raise ValueError('В каждом правиле нужен получатель default')
        for recipient in self.recipients.values():
            if recipient == 'employee':
                continue
            if (
                recipient.count('@') != 1
                or not all(recipient.split('@'))
                or any(character.isspace() for character in recipient)
            ):
                raise ValueError(
                    'Получатель должен быть email-адресом или значением employee'
                )
        return self


class InvoiceRoutingRules(BaseModel):
    """Непустой набор правил, каждое из которых применяется независимо."""

    model_config = ConfigDict(extra='forbid')

    rules: list[InvoiceRoutingRule] = Field(min_length=1)
