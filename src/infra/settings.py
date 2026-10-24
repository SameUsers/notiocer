from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class InvoiceReportFileSettings(BaseModel):
    """Настройки, описывающие исходный файл отчёта со счетами.

    Атрибуты:
        path: Путь к обрабатываемому отчёту Excel.
    """

    path: Path = Field(default=Path('workdir/DZ_Report.xls'))


class InvoiceSelectionSettings(BaseModel):
    """Настройки, управляющие отбором счетов для рассылки.

    Атрибуты:
        allowed_categories: Категории счетов, подходящие для рассылки.
        minimum_invoice_age: Минимальный возраст счёта, необходимый для его отбора.
    """

    allowed_categories: set[str] = {'Д0', 'Д1', 'Д2', 'Д3', 'Д4', 'Д5', 'Д60'}
    minimum_invoice_age: timedelta = timedelta(days=3)


class EmailMessageSettings(BaseModel):
    """Настройки исходящего письма рассылки.

    Атрибуты:
        mail_subject: Тема письма рассылки.
        mail_tex: Текст тела письма рассылки.
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
    """Учётные данные для учётной записи Exchange, используемой для отправки писем.

    Атрибуты:
        username: Адрес учётной записи Exchange.
        password: Пароль учётной записи Exchange.
    """

    username: str = 'some.email@highlevel.by'
    password: SecretStr = SecretStr('some_password')


class AxSettings(BaseModel):
    """Настройки подключения к базе данных Microsoft Dynamics AX.

    Атрибуты:
        odbc_driver: Имя используемого ODBC-драйвера.
        server: Хост сервера базы данных.
        database: Имя базы данных.
        username: Имя пользователя для аутентификации.
        password: Пароль для аутентификации.
    """

    odbc_driver: str = 'DRIVER'
    server: str = 'SERVER'
    database: str = 'DB_NAME'
    username: str = 'USERNAME'
    password: SecretStr = SecretStr('PASSWORD')


class AppSettings(BaseSettings):
    """Корневые настройки приложения, объединяющие все разделы конфигурации.

    Значения загружаются из переменных окружения и необязательного
    файла ``.env``, при этом вложенные разделы разделяются с помощью ``__``.

    Атрибуты:
        ax: Настройки подключения к базе данных AX.
        invoice_selection: Настройки отбора счетов.
        exchange: Настройки учётной записи Exchange.
        message: Настройки исходящего письма.
        invoice_report_file: Настройки исходного файла отчёта.
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
    """Возвращает кэшированные настройки приложения.

    Настройки загружаются один раз и переиспользуются при последующих вызовах.

    Returns:
        Экземпляр настроек приложения.
    """
    return AppSettings()
