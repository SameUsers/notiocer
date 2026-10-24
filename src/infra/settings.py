from datetime import timedelta
from functools import lru_cache

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class InvoiceSelectionSettings(BaseModel):
    allowed_categories: set[str] = {'Д0', 'Д1', 'Д2', 'Д3', 'Д4', 'Д5', 'Д60'}
    minimum_invoice_age: timedelta = timedelta(days=3)


class EmailMessageSettings(BaseModel):
    mail_subject: str = 'Неполученные предоплаты до загрузки'
    mail_tex: str = """Добрый день.
Направляем список счетов с неполученной в срок предоплатой до загрузки.
 
Условия контроля:
Оплата должна была поступить в течение 3 календарных дней с даты выставления счета. Счета, не оплаченные на 4-й календарный день, не включая текущий день, попадают в рассылку.
 
Просим незамедлительно обеспечить поступление оплаты от Клиента или предоставить СФБ пояснение и запланированную Клиентом дату платежа.
 
Неисполнение требований по своевременному получению предоплаты до загрузки ведет к ответственности в соответствии с Регламентом по работе с ДЗ и КЗ и Регламентом по финансовой безопасности сделок.
 
В случае некорректного отображения данных, ошибочного попадания счета в рассылку и/или невозможности получения оплаты по объективным причинам – просим сообщить об этом на почтовую группу СФБ."""


class ExchangeSettings(BaseModel):
    username: str = 'a.rusin@highlevel.by'
    password: SecretStr = SecretStr('n3Q47GEd')


class AxSettings(BaseModel):
    odbc_driver: str = 'ODBC Driver 17 for SQL Server'
    server: str = 'AXSQL2.sta.local'
    database: str = 'STA_Prod'
    username: str = 'qvWriter'
    password: SecretStr = SecretStr('qv_pa$$woRd')


class AppSettings(BaseSettings):
    ax: AxSettings = Field(default_factory=AxSettings)
    invoice_selection: InvoiceSelectionSettings = Field(
        default_factory=InvoiceSelectionSettings
    )
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    message: EmailMessageSettings = Field(default_factory=EmailMessageSettings)
    model_config = SettingsConfigDict(
        env_file='.env', case_sensitive=True, env_nested_delimiter='__'
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
