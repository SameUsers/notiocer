from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class InvoiceReportFileSettings(BaseModel):
    """Settings describing the source invoice report file.

    Attributes:
        path: Path to the Excel report to process.
    """

    path: Path = Field(default=Path('workdir/DZ_Report.xls'))


class InvoiceSelectionSettings(BaseModel):
    """Settings controlling which invoices are selected for mailing.

    Attributes:
        allowed_categories: Invoice categories eligible for mailing.
        minimum_invoice_age: Minimum age an invoice must have to be selected.
    """

    allowed_categories: set[str] = {'Д0', 'Д1', 'Д2', 'Д3', 'Д4', 'Д5', 'Д60'}
    minimum_invoice_age: timedelta = timedelta(days=3)


class EmailMessageSettings(BaseModel):
    """Settings for the outgoing mailing email.

    Attributes:
        mail_subject: Subject line of the mailing email.
        mail_tex: Body text of the mailing email.
    """

    mail_subject: str = 'Неполученные предоплаты до загрузки'
    mail_tex: str = """Добрый день.
Направляем список счетов с неполученной в срок предоплатой до загрузки.
 
Условия контроля:
Оплата должна была поступить в течение 3 календарных дней с даты выставления счета. Счета, не оплаченные на 4-й календарный день, не включая текущий день, попадают в рассылку.
 
Просим незамедлительно обеспечить поступление оплаты от Клиента или предоставить СФБ пояснение и запланированную Клиентом дату платежа.
 
Неисполнение требований по своевременному получению предоплаты до загрузки ведет к ответственности в соответствии с Регламентом по работе с ДЗ и КЗ и Регламентом по финансовой безопасности сделок.
 
В случае некорректного отображения данных, ошибочного попадания счета в рассылку и/или невозможности получения оплаты по объективным причинам – просим сообщить об этом на почтовую группу СФБ."""


class ExchangeSettings(BaseModel):
    """Credentials for the Exchange account used to send emails.

    Attributes:
        username: Exchange account address.
        password: Exchange account password.
    """

    username: str = 'a.rusin@highlevel.by'
    password: SecretStr = SecretStr('n3Q47GEd')


class AxSettings(BaseModel):
    """Connection settings for the Microsoft Dynamics AX database.

    Attributes:
        odbc_driver: Name of the ODBC driver to use.
        server: Database server host.
        database: Database name.
        username: Username for authentication.
        password: Password for authentication.
    """

    odbc_driver: str = 'ODBC Driver 17 for SQL Server'
    server: str = 'AXSQL2.sta.local'
    database: str = 'STA_Prod'
    username: str = 'qvWriter'
    password: SecretStr = SecretStr('qv_pa$$woRd')


class AppSettings(BaseSettings):
    """Root application settings aggregating all configuration sections.

    Values are loaded from environment variables and an optional
    ``.env`` file, with nested sections delimited by ``__``.

    Attributes:
        ax: AX database connection settings.
        invoice_selection: Invoice selection settings.
        exchange: Exchange account settings.
        message: Outgoing email settings.
        invoice_report_file: Source report file settings.
    """

    ax: AxSettings = Field(default_factory=AxSettings)
    invoice_selection: InvoiceSelectionSettings = Field(
        default_factory=InvoiceSelectionSettings
    )
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    message: EmailMessageSettings = Field(default_factory=EmailMessageSettings)
    model_config = SettingsConfigDict(
        env_file='.env', case_sensitive=True, env_nested_delimiter='__'
    )
    invoice_report_file: InvoiceReportFileSettings = Field(
        default_factory=InvoiceReportFileSettings
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return the cached application settings.

    The settings are loaded once and reused on subsequent calls.

    Returns:
        The application settings instance.
    """
    return AppSettings()
