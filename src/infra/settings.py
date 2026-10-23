from datetime import timedelta
from functools import lru_cache

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class InvoiceSelectionSettings(BaseModel):
    allowed_categories: set[str] = {"Д0", "Д1", "Д2", "Д3", "Д4", "Д5", "Д60"}
    minimum_invoice_age: timedelta = timedelta(days=3)

class EmailMessageSettings(BaseModel):
    mail_subject = "Неполученные предоплаты до загрузки"
    mail_tex = """Добрый день.
Направляем список счетов с неполученной в срок предоплатой до загрузки.
 
Условия контроля:
Оплата должна была поступить в течение 3 календарных дней с даты выставления счета. Счета, не оплаченные на 4-й календарный день, не включая текущий день, попадают в рассылку.
 
Просим незамедлительно обеспечить поступление оплаты от Клиента или предоставить СФБ пояснение и запланированную Клиентом дату платежа.
 
Неисполнение требований по своевременному получению предоплаты до загрузки ведет к ответственности в соответствии с Регламентом по работе с ДЗ и КЗ и Регламентом по финансовой безопасности сделок.
 
В случае некорректного отображения данных, ошибочного попадания счета в рассылку и/или невозможности получения оплаты по объективным причинам – просим сообщить об этом на почтовую группу СФБ."""

class ExchangeSettings(BaseModel):
    username: str = "a.rusin@highlevel.by"
    password: SecretStr = SecretStr("n3Q47GEd")


class AppSettings(BaseSettings):
    invoice_selection: InvoiceSelectionSettings = Field(default_factory=InvoiceSelectionSettings)
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    message: EmailMessageSettings = Field(default_factory=EmailMessageSettings)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_nested_delimiter="__"
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

